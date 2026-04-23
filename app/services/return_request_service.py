"""ReturnRequest service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.return_request import ReturnRequest
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.book import Book
from app.schemas.return_request import ReturnRequestAdminRow, ReturnRequestCreate
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

    async def list_admin(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ) -> List[ReturnRequestAdminRow]:
        rows = await self.repository.list_for_admin(
            db,
            skip=skip,
            limit=limit,
            status=status,
            from_dt=from_dt,
            to_dt=to_dt,
        )
        out: List[ReturnRequestAdminRow] = []
        for req in rows:
            buyer_email = None
            buyer_full_name = None
            if req.order and req.order.user:
                buyer_email = req.order.user.email
                buyer_full_name = req.order.user.full_name
            book_title = None
            if req.order_item:
                book_title = req.order_item.book_title
                bk = getattr(req.order_item, "book", None)
                if bk is not None and bk.title:
                    book_title = bk.title
            rs = req.status
            status_str = rs.value if hasattr(rs, "value") else str(rs)
            payload = {
                "id": req.id,
                "order_id": req.order_id,
                "order_item_id": req.order_item_id,
                "quantity": req.quantity,
                "reason": req.reason,
                "request_date": req.request_date,
                "processed_date": req.processed_date,
                "status": status_str,
                "processed_by": req.processed_by,
                "buyer_email": buyer_email,
                "buyer_full_name": buyer_full_name,
                "book_title": book_title,
            }
            out.append(ReturnRequestAdminRow.model_validate(payload))
        return out

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
