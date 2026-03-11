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
        """Lấy order kèm order_items + status_history."""
        result = await db.execute(
            select(Order)
            .where(Order.id == id)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.status_history),
            )
        )
        return result.scalars().first()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Order]:
        """Lấy đơn hàng của user (chưa xóa), có thể lọc theo status."""
        stmt = (
            select(Order)
            .where(
                Order.user_id == user_id,
                Order.deleted_at.is_(None),
            )
        )
        if status:
            stmt = stmt.where(Order.status == status)
        stmt = stmt.order_by(Order.order_date.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_orders(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Order]:
        """Admin: lấy tất cả đơn hàng, có thể lọc theo status."""
        stmt = select(Order).where(Order.deleted_at.is_(None))
        if status:
            stmt = stmt.where(Order.status == status)
        stmt = stmt.order_by(Order.order_date.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


order_repository = OrderRepository(Order)
