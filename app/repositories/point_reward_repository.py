"""Point reward catalog."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.point_reward import PointReward


class PointRewardRepository:
    async def get(self, db: AsyncSession, reward_id: int) -> Optional[PointReward]:
        r = await db.execute(select(PointReward).where(PointReward.id == reward_id))
        return r.scalars().first()

    async def list_active(self, db: AsyncSession) -> List[PointReward]:
        r = await db.execute(
            select(PointReward)
            .where(PointReward.active.is_(True))
            .order_by(PointReward.cost_points.asc())
        )
        return list(r.scalars().all())

    async def list_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 200
    ) -> List[PointReward]:
        r = await db.execute(
            select(PointReward)
            .order_by(PointReward.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(r.scalars().all())

    async def create(self, db: AsyncSession, row: PointReward) -> PointReward:
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    async def update_fields(
        self, db: AsyncSession, reward_id: int, data: dict
    ) -> Optional[PointReward]:
        row = await self.get(db, reward_id)
        if not row:
            return None
        for k, v in data.items():
            setattr(row, k, v)
        await db.flush()
        await db.refresh(row)
        return row


point_reward_repository = PointRewardRepository()
