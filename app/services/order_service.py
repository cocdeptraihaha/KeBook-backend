"""Order service."""
from datetime import datetime
from typing import List, Optional, Iterable, Tuple
from sqlalchemy import select
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
        return order

    async def get_user_orders(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> List[Order]:
        orders = await self.repository.get_by_user(db, user_id, skip, limit, status=status)
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
        self, db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> List[Order]:
        """Admin: lấy tất cả đơn."""
        return await self.repository.get_all_orders(db, skip, limit, status=status)

    # ── build order items ────────────────────────────────────

    async def _build_order_items(
        self,
        db: AsyncSession,
        user_id: int,
        items_spec: Iterable[Tuple[int, int]],
    ) -> Tuple[list[tuple[int, int, float]], float]:
        book_ids = {book_id for book_id, _ in items_spec}
        if not book_ids:
            raise ValueError("No items to checkout")

        result_books = await db.execute(
            select(Book).options(selectinload(Book.discounts)).where(Book.id.in_(book_ids))
        )
        books_by_id: dict[int, Book] = {b.id: b for b in result_books.scalars().all()}

        subtotal = 0.0
        order_items_data: list[tuple[int, int, float]] = []
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
            order_items_data.append((book_id, qty, price))
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
            promo, discount_amount, err = await promotion_service.validate_code(db, checkout_in.promotion_code, subtotal)
            if err:
                raise ValueError(err)
            if promo:
                promotion_id = promo.id

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

        for book_id, qty, price in order_items_data:
            db.add(OrderItem(order_id=order.id, book_id=book_id, quantity=qty, price=price))
            book = await db.get(Book, book_id)
            if book:
                book.stock_quantity = (book.stock_quantity or 0) - qty

        if promotion_id:
            db.add(OrderPromotion(order_id=order.id, promotion_id=promotion_id, discount_amount=discount_amount))

        for item in used_cart_items:
            await db.delete(item)

        self._add_history(db, order.id, "PENDING", "Đơn hàng mới")
        await db.flush()
        await db.refresh(order)
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
            return order, "cancelled"

        order.status = "CANCEL_REQUESTED"
        self._add_history(db, order.id, "CANCEL_REQUESTED", reason or "Yêu cầu hủy đơn")
        await db.flush()
        await db.refresh(order)
        return order, "cancel_requested"


order_service = OrderService()
