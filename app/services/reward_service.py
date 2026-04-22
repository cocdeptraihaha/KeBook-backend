"""Đổi điểm tích lũy lấy voucher (Promotion cá nhân)."""
import secrets
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotion import Promotion
from app.repositories.point_reward_repository import point_reward_repository
from app.services.points_service import points_service


class RewardService:
    async def redeem(
        self, db: AsyncSession, user_id: int, reward_id: int
    ) -> tuple[Promotion, int]:
        reward = await point_reward_repository.get(db, reward_id)
        if not reward or not reward.active:
            raise ValueError("Phần thưởng không tồn tại hoặc đã tắt")
        await points_service.subtract_points(
            db,
            user_id,
            reward.cost_points,
            reason=points_service.REASON_REDEEM,
            ref_type="point_reward",
            ref_id=reward.id,
        )
        now = datetime.utcnow()
        end = now + timedelta(days=max(1, int(reward.valid_days or 30)))
        code = f"PT{user_id}U{secrets.token_hex(4).upper()}"
        name = f"{reward.name} (đổi điểm)"
        promo = Promotion(
            owner_user_id=user_id,
            code=code,
            name=name,
            discount_percent=float(reward.discount_percent),
            max_discount=reward.max_discount,
            start_date=now,
            end_date=end,
            deleted_at=None,
        )
        db.add(promo)
        await db.flush()
        await db.refresh(promo)
        bal = await points_service.get_balance(db, user_id)
        return promo, bal


reward_service = RewardService()
