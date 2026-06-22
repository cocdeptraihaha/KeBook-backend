"""Order service."""
from datetime import datetime, timedelta
from typing import List, Optional, Iterable, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_promotion import OrderPromotion
from app.models.order_status_history import OrderStatusHistory, OrderHistoryStatus
from app.models.payment import Payment, PaymentMethod
from app.models.service import Service
from app.models.cart import Cart
from app.models.book import Book
from app.models.user import User
from app.models.user_address import UserAddress
from app.models.user_promotion import UserPromotion
from app.schemas.book import BookDiscountOut, _pick_active_discount
from app.schemas.order import OrderCreate, CheckoutRequest
from app.core.config import get_settings
from app.repositories.order_repository import order_repository
from app.repositories.cart_repository import cart_repository
from app.repositories.promotion_repository import promotion_repository
from app.services.promotion_service import promotion_service
from app.services.points_service import points_service

AUTO_CONFIRM_SECONDS = 30 * 60

STATUS_MAP = {
    "CANCELLED": OrderHistoryStatus.CANCELLED,
    "CANCEL_REQUESTED": OrderHistoryStatus.CANCEL_REQUESTED,
    "COMPLETED": OrderHistoryStatus.COMPLETED,
    "CONFIRMED": OrderHistoryStatus.CONFIRMED,
    "DELIVERED": OrderHistoryStatus.DELIVERED,
    "INPROGRESS": OrderHistoryStatus.INPROGRESS,
    "PENDING": OrderHistoryStatus.PENDING,
    "PROCESSING": OrderHistoryStatus.PROCESSING,
    "RETURNED": OrderHistoryStatus.RETURNED,
    "SHIPPED": OrderHistoryStatus.SHIPPED,
}

VALID_STATUSES = set(STATUS_MAP.keys())
NEXT_PROGRESS_STATUS = {
    "PENDING": "CONFIRMED",
    "CONFIRMED": "INPROGRESS",
    "INPROGRESS": "SHIPPED",
    "SHIPPED": "DELIVERED",
    "DELIVERED": "COMPLETED",
}
CANCELLABLE_BY_ADMIN = {"PENDING", "CONFIRMED", "INPROGRESS", "SHIPPED"}


class OrderService:
    """Logic nghiệp vụ cho Order."""

    def __init__(self):
        self.repository = order_repository

    # ── helpers ──────────────────────────────────────────────

    def _add_history(
        self,
        db: AsyncSession,
        order_id: int,
        status: str,
        description: Optional[str] = None,
    ):
        hist_enum = STATUS_MAP.get(status, OrderHistoryStatus.PENDING)
        hist = OrderStatusHistory(
            order_id=order_id,
            e_order_history=hist_enum,
            status_change_date=datetime.utcnow(),
            description=description,
        )
        db.add(hist)

    async def _restore_stock(self, db: AsyncSession, order: Order):
        """Cộng lại số lượng sách vào kho khi đơn bị hủy."""
        if not order.order_items:
            return
        book_ids = {item.book_id for item in order.order_items if item.book_id}
        if not book_ids:
            return
        result_books = await db.execute(
            select(Book).where(Book.id.in_(book_ids))
        )
        books_map = {b.id: b for b in result_books.scalars().all()}
        for item in order.order_items:
            if item.book_id:
                book = books_map.get(item.book_id)
                if book:
                    book.stock_quantity = (book.stock_quantity or 0) + (item.quantity or 0)

    async def auto_confirm_if_needed(self, db: AsyncSession, order: Order) -> Order:
        """Lazy auto-confirm: nếu PENDING > 30 phút → CONFIRMED."""
        raw = str(order.status).replace("OrderStatus.", "")
        if raw != "PENDING":
            return order
        if not order.order_date:
            return order
        elapsed = (datetime.utcnow() - order.order_date).total_seconds()
        if elapsed < AUTO_CONFIRM_SECONDS:
            return order
        order.status = "CONFIRMED"
        self._add_history(db, order.id, "CONFIRMED", "Tự động xác nhận sau 30 phút")
        await db.flush()
        await db.refresh(order)
        from app.services.notification_service import notification_service

        await notification_service.notify_order_status_for_buyer(
            db, order.user_id, order.id, "CONFIRMED"
        )
        return order

    # ── CRUD ─────────────────────────────────────────────────

    async def create_order(
        self, db: AsyncSession, order_in: OrderCreate, user_id: int
    ) -> Order:
        payment = Payment(amount=0, method=PaymentMethod.COD, payment_status="PENDING")
        db.add(payment)
        await db.flush()

        result = await db.execute(select(Service).where(Service.deleted_at.is_(None)).limit(1))
        service = result.scalars().first()
        if not service:
            service = Service(name_service="Standard delivery", price=0, status=True)
            db.add(service)
            await db.flush()

        total = sum(item.price * item.quantity for item in order_in.items)
        order = Order(
            user_id=user_id,
            payment_id=payment.id,
            service_id=service.id,
            note=order_in.note,
            phone_number=order_in.phone_number,
            shipping_address=order_in.shipping_address,
            status="PENDING",
            total_price=total,
            order_date=datetime.utcnow(),
        )
        db.add(order)
        await db.flush()

        for item in order_in.items:
            db.add(OrderItem(order_id=order.id, book_id=item.book_id, quantity=item.quantity, price=item.price))
        self._add_history(db, order.id, "PENDING", "Đơn hàng mới")
        await db.flush()
        await db.refresh(order)
        from app.services.notification_service import notification_service

        await notification_service.notify_checkout_placed_for_buyer(db, user_id, order.id)
        await notification_service.notify_admins_new_order(db, order.id)
        return order

    async def get_user_orders(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[Order]:
        orders = await self.repository.get_by_user(
            db, user_id, skip, limit, status=status, statuses=statuses
        )
        for o in orders:
            await self.auto_confirm_if_needed(db, o)
        return orders

    async def get_order(
        self, db: AsyncSession, order_id: int, user_id: Optional[int] = None
    ) -> Optional[Order]:
        order = await self.repository.get_with_items(db, order_id)
        if not order:
            return None
        if user_id and order.user_id != user_id:
            return None
        await self.auto_confirm_if_needed(db, order)
        return order

    async def get_all_orders(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        user_id: Optional[int] = None,
        q: Optional[str] = None,
    ) -> List[Order]:
        """Admin: lấy tất cả đơn (có thể lọc nâng cao)."""
        return await self.repository.get_all_orders(
            db,
            skip,
            limit,
            status=status,
            statuses=statuses,
            from_dt=from_dt,
            to_dt=to_dt,
            user_id=user_id,
            q=q,
        )

    def _history_status_str(self, hist: OrderStatusHistory) -> str:
        if hist.e_order_history is None:
            return ""
        v = hist.e_order_history
        return v.value if hasattr(v, "value") else str(v).split(".")[-1]

    def _previous_status_before_cancel_request(self, order: Order) -> Optional[str]:
        """Lấy trạng thái gần nhất trước CANCEL_REQUESTED (theo thời gian + id)."""
        hist = list(order.status_history or [])
        hist.sort(key=lambda h: (h.status_change_date or datetime.min, h.id or 0), reverse=True)
        if not hist:
            return "PENDING"
        i = 0
        while i < len(hist) and self._history_status_str(hist[i]) == "CANCEL_REQUESTED":
            i += 1
        if i < len(hist):
            return self._history_status_str(hist[i])
        return "PENDING"

    async def admin_resolve_cancel_request(
        self,
        db: AsyncSession,
        order_id: int,
        approve: bool,
        description: Optional[str] = None,
    ) -> Optional[Order]:
        """Duyệt hủy (→ CANCELLED) hoặc từ chối (khôi phục trạng thái trước đó)."""
        order = await self.repository.get_with_items(db, order_id)
        if not order:
            return None
        current = str(order.status).replace("OrderStatus.", "")
        if current != "CANCEL_REQUESTED":
            raise ValueError("Đơn không ở trạng thái yêu cầu hủy (CANCEL_REQUESTED)")

        from app.services.notification_service import notification_service

        if approve:
            order.status = "CANCELLED"
            self._add_history(
                db,
                order_id,
                "CANCELLED",
                description or "Admin chấp nhận hủy đơn",
            )
            await self._restore_stock(db, order)
            await db.flush()
            await db.refresh(order)
            await notification_service.notify_order_status_for_buyer(
                db, order.user_id, order.id, "CANCELLED"
            )
            return order

        prev = self._previous_status_before_cancel_request(order)
        if prev == "CANCEL_REQUESTED" or not prev:
            prev = "CONFIRMED"
        if prev not in VALID_STATUSES:
            prev = "CONFIRMED"
        order.status = prev
        self._add_history(
            db,
            order_id,
            prev,
            description or "Admin từ chối yêu cầu hủy đơn",
        )
        await db.flush()
        await db.refresh(order)
        await notification_service.notify_order_status_for_buyer(
            db, order.user_id, order.id, prev
        )
        return order

    # ── build order items ────────────────────────────────────

    async def _build_order_items(
        self,
        db: AsyncSession,
        user_id: int,
        items_spec: Iterable[Tuple[int, int]],
    ) -> Tuple[list[tuple[int, int, float, str]], float]:
        """Returns [(book_id, qty, price, book_title), ...] and subtotal."""
        book_ids = {book_id for book_id, _ in items_spec}
        if not book_ids:
            raise ValueError("No items to checkout")

        result_books = await db.execute(
            select(Book).options(selectinload(Book.discounts)).where(Book.id.in_(book_ids))
        )
        books_by_id: dict[int, Book] = {b.id: b for b in result_books.scalars().all()}

        subtotal = 0.0
        order_items_data: list[tuple[int, int, float, str]] = []
        for book_id, qty in items_spec:
            if qty <= 0:
                raise ValueError("Quantity must be positive")
            book = books_by_id.get(book_id)
            if not book or book.deleted_at is not None:
                raise ValueError(f"Book id={book_id} not found")
            original_price = book.selling_price or 0
            discounts = [BookDiscountOut.model_validate(d) for d in (book.discounts or [])]
            _, discount_amt = _pick_active_discount(discounts, original_price)
            price = max(0.0, original_price - discount_amt)
            if (book.stock_quantity or 0) < qty:
                raise ValueError(f"Book '{book.title}' insufficient stock")
            subtotal += price * qty
            order_items_data.append((book_id, qty, price, book.title or ""))
        return order_items_data, subtotal

    # ── checkout ─────────────────────────────────────────────

    async def checkout_from_cart(
        self, db: AsyncSession, user_id: int, checkout_in: CheckoutRequest
    ):
        explicit_items = checkout_in.items or []
        used_cart_items: list[Cart] = []

        if explicit_items:
            items_spec = [(it.book_id, it.quantity) for it in explicit_items if it.book_id]
            if not items_spec:
                raise ValueError("No valid items to checkout")
            order_items_data, subtotal = await self._build_order_items(db, user_id, items_spec)
            checkout_book_ids = {bid for bid, _ in items_spec}
            cart_items = await cart_repository.get_by_user(db, user_id, limit=500)
            used_cart_items = [ci for ci in cart_items if ci.book_id in checkout_book_ids]
        else:
            cart_items = await cart_repository.get_by_user(db, user_id, limit=500)
            if not cart_items:
                raise ValueError("Cart is empty")
            used_cart_items = list(cart_items)
            items_spec = [(item.book_id, item.quantity or 1) for item in cart_items if item.book_id is not None]
            order_items_data, subtotal = await self._build_order_items(db, user_id, items_spec)

        discount_amount = 0.0
        promotion_id = None
        applied_promo = None
        if checkout_in.promotion_code:
            promo, discount_amount, err = await promotion_service.validate_code(
                db, checkout_in.promotion_code, subtotal, user_id=user_id
            )
            if err:
                raise ValueError(err)
            if promo:
                already_used = await db.execute(
                    select(UserPromotion).where(
                        and_(
                            UserPromotion.user_id == user_id,
                            UserPromotion.promotion_id == promo.id,
                            UserPromotion.order_id.is_not(None),
                        )
                    )
                )
                if already_used.scalars().first():
                    raise ValueError("Bạn đã sử dụng mã giảm giá này rồi")
                promotion_id = promo.id
                applied_promo = promo

        after_promo = max(0.0, subtotal - discount_amount)
        settings = get_settings()
        point_val = max(0.0001, float(settings.LOYALTY_POINT_VALUE_VND or 1.0))
        max_pct = min(100, max(0, int(settings.LOYALTY_MAX_ORDER_POINTS_DISCOUNT_PERCENT or 50)))
        requested_pts = max(0, int(checkout_in.loyalty_points_to_redeem or 0))
        actual_pts = 0
        points_discount_amount = 0.0
        if requested_pts > 0:
            cap_vnd = min(after_promo, after_promo * (max_pct / 100.0))
            max_pts = int(cap_vnd / point_val)
            bal = await points_service.get_balance(db, user_id)
            actual_pts = min(requested_pts, max_pts, bal)
            points_discount_amount = round(float(actual_pts) * point_val, 2)
            if points_discount_amount > after_promo:
                points_discount_amount = float(after_promo)
                actual_pts = int(after_promo / point_val) if point_val > 0 else 0

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        saved_address = None
        if checkout_in.address_id:
            address_result = await db.execute(
                select(UserAddress).where(
                    UserAddress.id == checkout_in.address_id,
                    UserAddress.user_id == user_id,
                    UserAddress.deleted_at.is_(None),
                )
            )
            saved_address = address_result.scalars().first()
            if not saved_address:
                raise ValueError("Address not found")

        user_full_name = (
            checkout_in.full_name.strip()
            if checkout_in.full_name and checkout_in.full_name.strip()
            else (
                saved_address.recipient_name
                if saved_address and saved_address.recipient_name
                else ((user.full_name if user else None) or None)
            )
        )

        result = await db.execute(select(Service).where(Service.deleted_at.is_(None)).limit(1))
        service = result.scalars().first()
        if not service:
            service = Service(name_service="Standard delivery", price=0, status=True)
            db.add(service)
            await db.flush()
        shipping_fee = float(service.price or 0)
        if applied_promo and bool(getattr(applied_promo, "free_shipping", False)):
            shipping_fee = 0.0

        total = max(0.0, after_promo - points_discount_amount + shipping_fee)

        method_str = (checkout_in.payment_method or "COD").upper()
        if method_str == "VNPAY":
            pay_method = PaymentMethod.VNPAY
        elif method_str == "BANK_TRANSFER":
            pay_method = PaymentMethod.BANK_TRANSFER
        else:
            pay_method = PaymentMethod.COD

        payment = Payment(amount=total, method=pay_method, payment_status="PENDING")
        db.add(payment)
        await db.flush()

        phone_number = (
            checkout_in.phone_number.strip()
            if checkout_in.phone_number and checkout_in.phone_number.strip()
            else (
                saved_address.phone_number
                if saved_address and saved_address.phone_number
                else None
            )
        )
        address_detail = (
            checkout_in.shipping_address.strip()
            if checkout_in.shipping_address and checkout_in.shipping_address.strip()
            else (
                saved_address.address_detail
                if saved_address and saved_address.address_detail
                else ""
            )
        )
        ward = (
            checkout_in.ward.strip()
            if checkout_in.ward and checkout_in.ward.strip()
            else (saved_address.ward if saved_address and saved_address.ward else "")
        )
        province = (
            checkout_in.province.strip()
            if checkout_in.province and checkout_in.province.strip()
            else (saved_address.province if saved_address and saved_address.province else "")
        )
        address_parts = [address_detail, ward, province]
        full_address = ", ".join([p for p in address_parts if p]) or None

        order = Order(
            user_id=user_id,
            address_id=saved_address.id if saved_address else None,
            full_name=user_full_name,
            payment_id=payment.id,
            service_id=service.id,
            note=checkout_in.note,
            phone_number=phone_number,
            shipping_address=full_address,
            status="PENDING",
            total_price=total,
            order_date=datetime.utcnow(),
        )
        db.add(order)
        await db.flush()

        result_books = await db.execute(
            select(Book).where(Book.id.in_([bid for bid, _, _, _ in order_items_data]))
        )
        books_map = {b.id: b for b in result_books.scalars().all()}
        for book_id, qty, price, title in order_items_data:
            db.add(OrderItem(
                order_id=order.id, book_id=book_id, quantity=qty,
                price=price, book_title=title,
            ))
            book = books_map.get(book_id)
            if book:
                book.stock_quantity = (book.stock_quantity or 0) - qty

        if promotion_id:
            db.add(OrderPromotion(order_id=order.id, promotion_id=promotion_id, discount_amount=discount_amount))
            db.add(UserPromotion(
                user_id=user_id, promotion_id=promotion_id,
                order_id=order.id, used_at=datetime.utcnow(),
            ))
            pr = await promotion_repository.get(db, promotion_id)
            if pr:
                pr.used_count = int(pr.used_count or 0) + 1

        if actual_pts > 0:
            await points_service.subtract_points(
                db,
                user_id,
                actual_pts,
                reason=points_service.REASON_ORDER_CHECKOUT,
                ref_type="order",
                ref_id=order.id,
            )

        for item in used_cart_items:
            await db.delete(item)

        self._add_history(db, order.id, "PENDING", "Đơn hàng mới")
        await db.flush()
        await db.refresh(order)
        from app.services.notification_service import notification_service

        await notification_service.notify_checkout_placed_for_buyer(db, user_id, order.id)
        await notification_service.notify_admins_new_order(db, order.id)
        return (
            order,
            subtotal,
            discount_amount,
            shipping_fee,
            total,
            actual_pts,
            points_discount_amount,
        )

    # ── update status (admin) ────────────────────────────────

    async def update_status(
        self,
        db: AsyncSession,
        order_id: int,
        new_status: str,
        admin_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Optional[Order]:
        if new_status not in VALID_STATUSES:
            return None
        order = await self.repository.get(db, order_id)
        if not order:
            return None
        current = str(order.status).replace("OrderStatus.", "")
        if current == new_status:
            return order

        terminal_states = {"CANCELLED", "COMPLETED", "RETURNED"}
        if current in terminal_states:
            raise ValueError(f"Không thể đổi trạng thái từ {current}")

        if new_status == "CANCELLED":
            if current not in CANCELLABLE_BY_ADMIN:
                raise ValueError(f"Không thể hủy đơn ở trạng thái {current}")
            # Load items to ensure we can restore stock
            order_full = await self.repository.get_with_items(db, order_id)
            if order_full:
                await self._restore_stock(db, order_full)
        elif current == "DELIVERED" and new_status == "RETURNED":
            # Allow direct transition from DELIVERED to RETURNED
            pass
        else:
            expected_next = NEXT_PROGRESS_STATUS.get(current)
            if expected_next is None or new_status != expected_next:
                raise ValueError(
                    f"Chỉ được xúc tiến trạng thái kế tiếp từ {current} sang {expected_next or 'N/A'}"
                )

        order.status = new_status
        self._add_history(db, order_id, new_status, description)

        # Award loyalty points if order is completed: 1 point per 10,000 VND order value
        if new_status == "COMPLETED" and order.total_price and order.total_price >= 10000:
            points_to_award = int(order.total_price // 10000)
            if points_to_award > 0:
                await points_service.add_points(
                    db,
                    user_id=order.user_id,
                    delta=points_to_award,
                    reason=points_service.REASON_ORDER_COMPLETE,
                    ref_type="order",
                    ref_id=order.id,
                )

        await db.flush()
        await db.refresh(order)
        from app.services.notification_service import notification_service

        raw = str(new_status).replace("OrderStatus.", "")
        await notification_service.notify_order_status_for_buyer(
            db, order.user_id, order.id, raw
        )
        return order

    async def update_shipment(
        self,
        db: AsyncSession,
        order_id: int,
        *,
        tracking_number: Optional[str] = None,
        shipping_provider: Optional[str] = None,
    ) -> Optional[Order]:
        """Admin: cập nhật mã vận đơn / đơn vị vận chuyển."""
        order = await self.repository.get(db, order_id)
        if not order:
            return None
        if tracking_number is not None:
            order.tracking_number = tracking_number
        if shipping_provider is not None:
            order.shipping_provider = shipping_provider
        await db.flush()
        await db.refresh(order)
        from app.services.notification_service import notification_service
        from app.schemas.notification import NotificationType

        await notification_service.create_and_send_to_users(
            db,
            [order.user_id],
            title=f"ORDER #{order_id}",
            type=NotificationType.ORDER_SHIPMENT.value,
            payload={
                "order_id": order_id,
                "tracking_number": order.tracking_number,
                "shipping_provider": order.shipping_provider,
            },
        )
        return order

    # ── cancel / request cancel (user) ───────────────────────

    async def cancel_or_request_cancel(
        self,
        db: AsyncSession,
        order_id: int,
        user_id: int,
        reason: Optional[str] = None,
    ) -> Tuple[Order, str]:
        """Hủy đơn hoặc gửi yêu cầu hủy. Trả về (order, action)."""
        order = await self.repository.get_with_items(db, order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Order not found")

        current = str(order.status).replace("OrderStatus.", "")
        terminal = {"CANCELLED", "COMPLETED", "DELIVERED", "RETURNED", "CANCEL_REQUESTED"}
        if current in terminal:
            raise ValueError(f"Không thể hủy đơn ở trạng thái {current}")

        now = datetime.utcnow()
        elapsed = (now - order.order_date).total_seconds() if order.order_date else float("inf")

        if current in ("PENDING", "CONFIRMED") and elapsed <= AUTO_CONFIRM_SECONDS:
            order.status = "CANCELLED"
            self._add_history(db, order.id, "CANCELLED", reason or "Người dùng hủy đơn")
            await self._restore_stock(db, order)
            await db.flush()
            await db.refresh(order)
            from app.services.notification_service import notification_service

            await notification_service.notify_order_status_for_buyer(
                db, order.user_id, order.id, "CANCELLED"
            )
            return order, "cancelled"

        order.status = "CANCEL_REQUESTED"
        self._add_history(db, order.id, "CANCEL_REQUESTED", reason or "Yêu cầu hủy đơn")
        await db.flush()
        await db.refresh(order)
        from app.services.notification_service import notification_service

        await notification_service.notify_order_status_for_buyer(
            db, order.user_id, order.id, "CANCEL_REQUESTED"
        )
        return order, "cancel_requested"

    async def get_money_stats(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ):
        """Gom nhóm tiền + số đơn theo bucket trạng thái (user cụ thể hoặc toàn shop nếu user_id=None)."""
        from app.schemas.order import MoneyBucket, OrderMoneyStats

        stmt = select(
            Order.status,
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_price), 0.0),
        ).where(Order.deleted_at.is_(None))
        if user_id is not None:
            stmt = stmt.where(Order.user_id == user_id)
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        stmt = stmt.group_by(Order.status)
        result = await db.execute(stmt)
        rows = result.all()

        def norm_status(cell) -> str:
            if cell is None:
                return ""
            r = str(cell)
            return r.split(".")[-1] if "." in r else r

        per: dict[str, tuple[int, float]] = {}
        for status_cell, cnt, total in rows:
            key = norm_status(status_cell)
            per[key] = (int(cnt), float(total or 0))

        def bucket(status_keys: List[str]) -> tuple[int, float]:
            c, t = 0, 0.0
            for s in status_keys:
                if s in per:
                    cc, tt = per[s]
                    c += cc
                    t += tt
            return c, t

        pc = bucket(["PENDING", "CONFIRMED"])
        sh = bucket(["INPROGRESS", "SHIPPED"])
        dv = bucket(["DELIVERED", "COMPLETED"])
        cx = bucket(["CANCELLED", "CANCEL_REQUESTED", "RETURNED"])

        return OrderMoneyStats(
            pending_confirm=MoneyBucket(count=pc[0], total=pc[1]),
            shipping=MoneyBucket(count=sh[0], total=sh[1]),
            delivered=MoneyBucket(count=dv[0], total=dv[1]),
            cancelled=MoneyBucket(count=cx[0], total=cx[1]),
            total_spent=float(dv[1]),
        )

    async def get_user_money_stats(
        self,
        db: AsyncSession,
        user_id: int,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ):
        """Gom nhóm tiền + số đơn theo bucket trạng thái (một user)."""
        return await self.get_money_stats(db, user_id=user_id, from_dt=from_dt, to_dt=to_dt)

    async def get_revenue_timeseries(
        self,
        db: AsyncSession,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        group_by: str = "day",
    ) -> List[dict]:
        """Chuỗi doanh thu theo ngày/tuần/tháng (chỉ DELIVERED + COMPLETED)."""
        from app.models.order import OrderStatus

        gb = (group_by or "day").lower()
        if gb == "day":
            # Flexible date range calculation for dashboard chart.
            # Missing days are returned with zero values.
            end = to_dt or datetime.utcnow()
            end_day = datetime(end.year, end.month, end.day, 23, 59, 59, 999999)
            if from_dt is not None:
                start_day = datetime(from_dt.year, from_dt.month, from_dt.day)
            else:
                start_day = datetime(end.year, end.month, end.day) - timedelta(days=13)

            # Limit window size to 366 days max to protect resources
            diff_days = (end_day - start_day).days + 1
            if diff_days <= 0:
                diff_days = 1
            elif diff_days > 366:
                diff_days = 366
                start_day = end_day - timedelta(days=365)

            period_expr = func.date(Order.order_date)
            stmt = (
                select(
                    period_expr.label("period"),
                    func.count(Order.id),
                    func.coalesce(func.sum(Order.total_price), 0.0),
                )
                .where(
                    Order.deleted_at.is_(None),
                    Order.status.in_([OrderStatus.DELIVERED, OrderStatus.COMPLETED]),
                    Order.order_date >= start_day,
                    Order.order_date <= end_day,
                )
                .group_by(period_expr)
                .order_by(period_expr)
            )
            result = await db.execute(stmt)
            data_by_period: dict[str, tuple[int, float]] = {}
            for period, cnt, total in result.all():
                key = period.isoformat() if hasattr(period, "isoformat") else str(period)
                data_by_period[key] = (int(cnt), float(total or 0))

            out: List[dict] = []
            for i in range(diff_days):
                day = start_day + timedelta(days=i)
                key = day.date().isoformat()
                cnt, total = data_by_period.get(key, (0, 0.0))
                out.append(
                    {
                        "period": key,
                        "order_count": cnt,
                        "revenue": total,
                    }
                )
            return out

        if gb == "year":
            period_expr = func.date_format(Order.order_date, "%Y")
        elif gb == "quarter":
            period_expr = func.concat(func.year(Order.order_date), "-Q", func.quarter(Order.order_date))
        elif gb == "month":
            period_expr = func.date_format(Order.order_date, "%Y-%m-01")
        elif gb == "week":
            period_expr = func.date_format(Order.order_date, "%X-W%V")
        else:
            period_expr = func.date(Order.order_date)

        stmt = (
            select(
                period_expr.label("period"),
                func.count(Order.id),
                func.coalesce(func.sum(Order.total_price), 0.0),
            )
            .where(
                Order.deleted_at.is_(None),
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.COMPLETED]),
            )
            .group_by(period_expr)
            .order_by(period_expr)
        )
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        result = await db.execute(stmt)
        out: List[dict] = []
        for period, cnt, total in result.all():
            p = period
            if hasattr(p, "isoformat"):
                p = p.isoformat()
            elif p is not None:
                p = str(p)
            else:
                p = ""
            out.append(
                {
                    "period": p,
                    "order_count": int(cnt),
                    "revenue": float(total or 0),
                }
            )
        return out


order_service = OrderService()
