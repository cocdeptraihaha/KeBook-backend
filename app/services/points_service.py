"""Điểm tích lũy: cộng/trừ atomic + ghi lịch sử."""
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import User
from app.repositories.point_transaction_repository import point_transaction_repository


class PointsService:
    REASON_REVIEW = "REVIEW_REWARD"
    REASON_REDEEM = "REDEEM_VOUCHER"
    REASON_ADMIN = "ADMIN_ADJUST"

    async def get_balance(self, db: AsyncSession, user_id: int) -> int:
        r = await db.execute(
            select(func.coalesce(User.loyalty_points, 0)).where(User.id == user_id)
        )
        v = r.scalar_one_or_none()
        return int(v or 0)

    async def add_points(
        self,
        db: AsyncSession,
        user_id: int,
        delta: int,
        *,
        reason: str,
        ref_type: str | None = None,
        ref_id: int | None = None,
    ) -> int:
        if delta <= 0:
            raise ValueError("delta must be positive")
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(loyalty_points=func.coalesce(User.loyalty_points, 0) + delta)
        )
        await db.flush()
        bal = await self.get_balance(db, user_id)
        await point_transaction_repository.create(
            db,
            user_id=user_id,
            delta=delta,
            reason=reason,
            ref_type=ref_type,
            ref_id=ref_id,
            balance_after=bal,
        )
        return bal

    async def subtract_points(
        self,
        db: AsyncSession,
        user_id: int,
        amount: int,
        *,
        reason: str,
        ref_type: str | None = None,
        ref_id: int | None = None,
    ) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")
        res = await db.execute(
            update(User)
            .where(
                User.id == user_id,
                func.coalesce(User.loyalty_points, 0) >= amount,
            )
            .values(loyalty_points=func.coalesce(User.loyalty_points, 0) - amount)
        )
        if res.rowcount == 0:
            raise ValueError("Không đủ điểm tích lũy")
        await db.flush()
        bal = await self.get_balance(db, user_id)
        await point_transaction_repository.create(
            db,
            user_id=user_id,
            delta=-amount,
            reason=reason,
            ref_type=ref_type,
            ref_id=ref_id,
            balance_after=bal,
        )
        return bal

    async def award_for_new_review(
        self, db: AsyncSession, user_id: int, review_id: int
    ) -> int:
        settings = get_settings()
        n = max(0, int(settings.REVIEW_REWARD_POINTS or 0))
        if n == 0:
            return await self.get_balance(db, user_id)
        return await self.add_points(
            db,
            user_id,
            n,
            reason=self.REASON_REVIEW,
            ref_type="review",
            ref_id=review_id,
        )


points_service = PointsService()
