"""ReturnRequest service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.return_request import ReturnRequest
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.book import Book
from app.schemas.return_request import ReturnRequestCreate, ReturnRequestUpdate
from app.repositories.return_request_repository import return_request_repository


class ReturnRequestService:
    """Logic nghiệp vụ cho ReturnRequest."""

    def __init__(self):
        self.repository = return_request_repository

    async def create(
        self, db: AsyncSession, req_in: ReturnRequestCreate, user_id: int
    ) -> ReturnRequest:
        """User tạo yêu cầu trả hàng."""
        # Kiểm tra order thuộc user
        order = await db.get(Order, req_in.order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Order not found or does not belong to you")
        if order.status not in ("COMPLETED", "DELIVERED"):
            raise ValueError("Return request only allowed when order is delivered")

        order_item = await db.get(OrderItem, req_in.order_item_id)
        if not order_item or order_item.order_id != req_in.order_id:
            raise ValueError("Product does not belong to order")
        if req_in.quantity > (order_item.quantity or 0):
            raise ValueError("Return quantity exceeds purchased quantity")

        data = req_in.model_dump()
        data["request_date"] = datetime.utcnow()
        data["status"] = "PENDING"
        return await self.repository.create(db, ReturnRequestCreate(**data))

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
            # Hoàn tồn kho
            oi = await db.get(OrderItem, req.order_item_id)
            if oi and oi.book_id:
                book = await db.get(Book, oi.book_id)
                if book:
                    book.stock_quantity = (book.stock_quantity or 0) + req.quantity
        await db.flush()
        await db.refresh(req)
        return req


return_request_service = ReturnRequestService()
