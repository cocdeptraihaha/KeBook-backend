"""Order service."""
from datetime import datetime
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
from app.models.user_promotion import UserPromotion
from app.schemas.book import BookDiscountOut, _pick_active_discount
from app.schemas.order import OrderCreate, CheckoutRequest
from app.repositories.order_repository import order_repository
from app.repositories.cart_repository import cart_repository
from app.services.promotion_service import promotion_service

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

        if checkout_in.full_name and checkout_in.full_name.strip():
            user_full_name = checkout_in.full_name.strip()
        else:
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalars().first()
            user_full_name = (user.full_name if user else None) or None

        result = await db.execute(select(Service).where(Service.deleted_at.is_(None)).limit(1))
        service = result.scalars().first()
        if not service:
            service = Service(name_service="Standard delivery", price=0, status=True)
            db.add(service)
            await db.flush()
        shipping_fee = float(service.price or 0)

        total = max(0.0, subtotal - discount_amount + shipping_fee)

        payment = Payment(amount=total, method=PaymentMethod.COD, payment_status="PENDING")
        db.add(payment)
        await db.flush()

        address_parts = [
            (checkout_in.shipping_address or "").strip(),
            (checkout_in.ward or "").strip(),
            (checkout_in.province or "").strip(),
        ]
        full_address = ", ".join([p for p in address_parts if p]) or None

        order = Order(
            user_id=user_id,
            full_name=user_full_name,
            payment_id=payment.id,
            service_id=service.id,
            note=checkout_in.note,
            phone_number=checkout_in.phone_number,
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

        for item in used_cart_items:
            await db.delete(item)

        self._add_history(db, order.id, "PENDING", "Đơn hàng mới")
        await db.flush()
        await db.refresh(order)
        from app.services.notification_service import notification_service

        await notification_service.notify_checkout_placed_for_buyer(db, user_id, order.id)
        await notification_service.notify_admins_new_order(db, order.id)
        return order, subtotal, discount_amount, shipping_fee, total

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
        order.status = new_status
        self._add_history(db, order_id, new_status, description)
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

        meta = f"tracking:{order.tracking_number or ''}|provider:{order.shipping_provider or ''}"
        await notification_service.create_and_send_to_users(
            db,
            [order.user_id],
            title=f"Đơn hàng #{order_id}",
            message=f"Đơn của bạn đã có thông tin vận chuyển.\n{meta}",
            type="ORDER_SHIPMENT",
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
        if gb == "month":
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
