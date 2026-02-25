"""ReturnRequest repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.return_request import ReturnRequest
from app.schemas.return_request import ReturnRequestCreate, ReturnRequestUpdate
from app.repositories.base_repository import BaseRepository


class ReturnRequestRepository(BaseRepository[ReturnRequest, ReturnRequestCreate, ReturnRequestUpdate]):
    """Repository cho ReturnRequest."""

    async def get_by_order(
        self, db: AsyncSession, order_id: int
    ) -> List[ReturnRequest]:
        result = await db.execute(
            select(ReturnRequest)
            .where(ReturnRequest.order_id == order_id)
            .options(selectinload(ReturnRequest.order_item))
        )
        return list(result.scalars().all())

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ReturnRequest]:
        from app.models.order import Order
        result = await db.execute(
            select(ReturnRequest)
            .join(ReturnRequest.order)
            .where(Order.user_id == user_id)
            .options(selectinload(ReturnRequest.order_item))
            .order_by(ReturnRequest.request_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ReturnRequest]:
        result = await db.execute(
            select(ReturnRequest)
            .where(ReturnRequest.status == "PENDING")
            .order_by(ReturnRequest.request_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


return_request_repository = ReturnRequestRepository(ReturnRequest)
