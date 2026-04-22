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


point_reward_repository = PointRewardRepository()
