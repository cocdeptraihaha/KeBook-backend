"""ReturnRequest service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.return_request import ReturnRequest
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.book import Book
from app.schemas.return_request import ReturnRequestCreate
from app.repositories.return_request_repository import return_request_repository
from app.repositories.order_repository import order_repository


class ReturnRequestService:
    """Logic nghiệp vụ cho ReturnRequest."""

    def __init__(self):
        self.repository = return_request_repository

    async def create(
        self, db: AsyncSession, req_in: ReturnRequestCreate, user_id: int
    ) -> ReturnRequest:
        """User tạo yêu cầu trả hàng."""
        order = await order_repository.get(db, req_in.order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Order not found or does not belong to you")

        raw_status = str(order.status).replace("OrderStatus.", "")
        if raw_status not in ("COMPLETED", "DELIVERED"):
            raise ValueError("Return request only allowed when order is delivered")

        result = await db.execute(
            select(OrderItem).where(OrderItem.id == req_in.order_item_id)
        )
        order_item = result.scalars().first()
        if not order_item or order_item.order_id != req_in.order_id:
            raise ValueError("Product does not belong to order")
        if req_in.quantity > (order_item.quantity or 0):
            raise ValueError("Return quantity exceeds purchased quantity")

        req = ReturnRequest(
            order_id=req_in.order_id,
            order_item_id=req_in.order_item_id,
            quantity=req_in.quantity,
            reason=req_in.reason,
            request_date=datetime.utcnow(),
            status="PENDING",
        )
        db.add(req)
        await db.flush()
        await db.refresh(req)
        return req

    async def get_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ReturnRequest]:
        return await self.repository.get_by_user(db, user_id, skip, limit)

    async def get_pending(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ReturnRequest]:
        return await self.repository.get_pending(db, skip, limit)

    async def process(
        self,
        db: AsyncSession,
        req_id: int,
        status: str,
        admin_id: int,
    ) -> Optional[ReturnRequest]:
        """Admin duyệt/từ chối yêu cầu trả hàng."""
        if status not in ("APPROVED", "REJECTED"):
            return None
        req = await self.repository.get(db, req_id)
        if not req or req.status != "PENDING":
            return None
        req.status = status
        req.processed_by = admin_id
        req.processed_date = datetime.utcnow()
        if status == "APPROVED":
            result = await db.execute(
                select(OrderItem).where(OrderItem.id == req.order_item_id)
            )
            oi = result.scalars().first()
            if oi and oi.book_id:
                book_result = await db.execute(
                    select(Book).where(Book.id == oi.book_id)
                )
                book = book_result.scalars().first()
                if book:
                    book.stock_quantity = (book.stock_quantity or 0) + req.quantity
        await db.flush()
        await db.refresh(req)
        return req


return_request_service = ReturnRequestService()
