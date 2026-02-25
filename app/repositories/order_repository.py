"""Order repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order, OrderCreate, OrderUpdate]):
    """Repository cho Order."""

    async def get_with_items(self, db: AsyncSession, id: int) -> Optional[Order]:
        """Lấy order kèm order_items."""
        result = await db.execute(
            select(Order)
            .where(Order.id == id)
            .options(selectinload(Order.order_items))
        )
        return result.scalars().first()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        """Lấy đơn hàng của user (chưa xóa)."""
        result = await db.execute(
            select(Order)
            .where(
                Order.user_id == user_id,
                Order.is_deleted == False,  # noqa: E712
            )
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


order_repository = OrderRepository(Order)
