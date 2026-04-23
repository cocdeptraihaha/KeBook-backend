"""Order repository."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
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
        statuses: Optional[List[str]] = None,
    ) -> List[Order]:
        """Lấy đơn hàng của user (chưa xóa), có thể lọc theo status hoặc nhiều status."""
        stmt = (
            select(Order)
            .where(
                Order.user_id == user_id,
                Order.deleted_at.is_(None),
            )
            .options(selectinload(Order.order_items))
        )
        if statuses:
            enums: List[OrderStatus] = []
            for s in statuses:
                key = (s or "").strip().upper()
                if key in OrderStatus.__members__:
                    enums.append(OrderStatus[key])
            if enums:
                stmt = stmt.where(Order.status.in_(enums))
        elif status:
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
        statuses: Optional[List[str]] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        user_id: Optional[int] = None,
        q: Optional[str] = None,
    ) -> List[Order]:
        """Admin: lấy tất cả đơn hàng; lọc status/status_in, khoảng ngày, user_id, tìm kiếm."""
        stmt = (
            select(Order)
            .where(Order.deleted_at.is_(None))
            .options(selectinload(Order.order_items))
        )
        if statuses:
            enums: List[OrderStatus] = []
            for s in statuses:
                key = (s or "").strip().upper()
                if key in OrderStatus.__members__:
                    enums.append(OrderStatus[key])
            if enums:
                stmt = stmt.where(Order.status.in_(enums))
        elif status:
            key = (status or "").strip().upper()
            if key in OrderStatus.__members__:
                stmt = stmt.where(Order.status == OrderStatus[key])
            else:
                stmt = stmt.where(Order.status == status)
        if from_dt is not None:
            stmt = stmt.where(Order.order_date >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(Order.order_date <= to_dt)
        if user_id is not None:
            stmt = stmt.where(Order.user_id == user_id)
        if q and q.strip():
            term = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Order.full_name.like(term),
                    Order.phone_number.like(term),
                    Order.shipping_address.like(term),
                )
            )
        stmt = stmt.order_by(Order.order_date.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


order_repository = OrderRepository(Order)
