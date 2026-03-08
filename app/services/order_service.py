"""Order service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_promotion import OrderPromotion
from app.models.order_status_history import OrderStatusHistory, OrderHistoryStatus
from app.models.payment import Payment, PaymentMethod
from app.models.service import Service
from app.models.cart import Cart
from app.models.book import Book
from app.schemas.order import OrderCreate, CheckoutRequest
from app.repositories.order_repository import order_repository
from app.repositories.cart_repository import cart_repository
from app.services.promotion_service import promotion_service


class OrderService:
    """Logic nghiệp vụ cho Order."""

    def __init__(self):
        self.repository = order_repository

    async def create_order(
        self, db: AsyncSession, order_in: OrderCreate, user_id: int
    ) -> Order:
        """Tạo đơn hàng mới."""
        payment = Payment(
            amount=0,
            method=PaymentMethod.COD,
            payment_status="PENDING",
        )
        db.add(payment)
        await db.flush()

        result = await db.execute(select(Service).where(Service.is_deleted == False).limit(1))
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
            oi = OrderItem(
                order_id=order.id,
                book_id=item.book_id,
                quantity=item.quantity,
                price=item.price,
            )
            db.add(oi)
        await db.flush()
        await db.refresh(order)
        return order

    async def get_user_orders(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        return await self.repository.get_by_user(db, user_id, skip, limit)

    async def get_order(
        self, db: AsyncSession, order_id: int, user_id: Optional[int] = None
    ) -> Optional[Order]:
        order = await self.repository.get_with_items(db, order_id)
        if not order:
            return None
        if user_id and order.user_id != user_id:
            return None
        return order

    async def checkout_from_cart(
        self, db: AsyncSession, user_id: int, checkout_in: CheckoutRequest
    ) -> Order:
        """Tạo đơn hàng từ giỏ hàng."""
        cart_items = await cart_repository.get_by_user(db, user_id, limit=500)
        if not cart_items:
            raise ValueError("Cart is empty")

        # Lấy giá sách, tính tổng, kiểm tra tồn kho
        subtotal = 0.0
        order_items_data = []
        for item in cart_items:
            book = await db.get(Book, item.book_id)
            if not book or book.is_deleted:
                raise ValueError(f"Book id={item.book_id} not found")
            price = book.selling_price or 0
            qty = item.quantity or 1
            if (book.stock_quantity or 0) < qty:
                raise ValueError(f"Book '{book.title}' insufficient stock")
            subtotal += price * qty
            order_items_data.append((item.book_id, qty, price))

        # Áp dụng promotion
        discount_amount = 0.0
        promotion_id = None
        if checkout_in.promotion_code:
            promo, discount_amount, err = await promotion_service.validate_code(
                db, checkout_in.promotion_code, subtotal
            )
            if err:
                raise ValueError(err)
            if promo:
                promotion_id = promo.id

        total = max(0, subtotal - discount_amount)

        # Tạo payment
        payment = Payment(
            amount=total,
            method=PaymentMethod.COD,
            payment_status="PENDING",
        )
        db.add(payment)
        await db.flush()

        # Lấy service
        result = await db.execute(
            select(Service).where(Service.is_deleted == False).limit(1)
        )
        service = result.scalars().first()
        if not service:
            service = Service(name_service="Standard delivery", price=0, status=True)
            db.add(service)
            await db.flush()

        # Tạo order
        order = Order(
            user_id=user_id,
            payment_id=payment.id,
            service_id=service.id,
            note=checkout_in.note,
            phone_number=checkout_in.phone_number,
            shipping_address=checkout_in.shipping_address,
            status="PENDING",
            total_price=total,
            order_date=datetime.utcnow(),
        )
        db.add(order)
        await db.flush()

        # Order items
        for book_id, qty, price in order_items_data:
            oi = OrderItem(order_id=order.id, book_id=book_id, quantity=qty, price=price)
            db.add(oi)
            # Trừ tồn kho
            book = await db.get(Book, book_id)
            if book:
                book.stock_quantity = (book.stock_quantity or 0) - qty

        # Order promotion
        if promotion_id:
            op = OrderPromotion(
                order_id=order.id,
                promotion_id=promotion_id,
                discount_amount=discount_amount,
            )
            db.add(op)

        # Soft delete cart items
        for item in cart_items:
            item.is_deleted = True
            item.deleted_at = datetime.utcnow()

        await db.flush()
        await db.refresh(order)
        return order

    async def update_status(
        self,
        db: AsyncSession,
        order_id: int,
        new_status: str,
        admin_id: Optional[int] = None,
    ) -> Optional[Order]:
        """Cập nhật trạng thái đơn (admin). Ghi lịch sử."""
        valid = {"PENDING", "CONFIRMED", "INPROGRESS", "SHIPPED", "DELIVERED", "COMPLETED", "CANCELLED", "RETURNED"}
        if new_status not in valid:
            return None
        order = await self.repository.get(db, order_id)
        if not order:
            return None
        old_status = order.status
        order.status = new_status

        # Map order status to history enum
        status_map = {
            "CANCELLED": OrderHistoryStatus.CANCELLED,
            "COMPLETED": OrderHistoryStatus.COMPLETED,
            "DELIVERED": OrderHistoryStatus.DELIVERED,
            "PENDING": OrderHistoryStatus.PENDING,
            "PROCESSING": OrderHistoryStatus.PROCESSING,
            "RETURNED": OrderHistoryStatus.RETURNED,
            "SHIPPED": OrderHistoryStatus.SHIPPED,
        }
        hist_status = status_map.get(new_status, OrderHistoryStatus.PENDING)
        hist = OrderStatusHistory(
            order_id=order_id,
            e_order_history=hist_status,
            status_change_date=datetime.utcnow(),
        )
        db.add(hist)
        await db.flush()
        await db.refresh(order)
        return order


order_service = OrderService()
