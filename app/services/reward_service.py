"""Redeem loyalty points for personal promotions."""
import secrets
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotion import Promotion
from app.repositories.point_reward_repository import point_reward_repository
from app.repositories.point_transaction_repository import point_transaction_repository
from app.services.points_service import points_service


VALID_REWARD_TYPES = {"DISCOUNT_PERCENT", "DISCOUNT_AMOUNT", "FREE_SHIPPING"}


class RewardService:
    async def redeem(
        self, db: AsyncSession, user_id: int, reward_id: int
    ) -> tuple[Promotion, int]:
        reward = await point_reward_repository.get(db, reward_id)
        if not reward or not reward.active:
            raise ValueError("Phan thuong khong ton tai hoac da tat")

        reward_type = (getattr(reward, "reward_type", None) or "DISCOUNT_PERCENT").upper()
        if reward_type not in VALID_REWARD_TYPES:
            raise ValueError("Loai phan thuong khong hop le")

        usage_limit = getattr(reward, "usage_limit", None)
        if usage_limit is not None and int(usage_limit) > 0:
            used = int(getattr(reward, "used_count", 0) or 0)
            if used >= int(usage_limit):
                raise ValueError("Phan thuong da het luot doi")

        already_redeemed = await point_transaction_repository.exists_for_ref(
            db,
            user_id=user_id,
            reason=points_service.REASON_REDEEM,
            ref_type="point_reward",
            ref_id=reward.id,
        )
        if already_redeemed:
            raise ValueError("Bạn đã đổi phần thưởng này trước đó")

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
        name = f"{reward.name}"
        promo = Promotion(
            owner_user_id=user_id,
            code=code,
            name=name,
            discount_percent=(
                float(reward.discount_percent or 0)
                if reward_type == "DISCOUNT_PERCENT"
                else None
            ),
            discount_amount=(
                float(reward.discount_amount or 0)
                if reward_type == "DISCOUNT_AMOUNT"
                else None
            ),
            free_shipping=reward_type == "FREE_SHIPPING",
            max_discount=reward.max_discount,
            min_order_amount=getattr(reward, "min_order_amount", None),
            usage_limit=1,
            used_count=0,
            start_date=now,
            end_date=end,
            deleted_at=None,
        )
        db.add(promo)
        reward.used_count = int(getattr(reward, "used_count", 0) or 0) + 1
        await db.flush()
        await db.refresh(promo)
        bal = await points_service.get_balance(db, user_id)
        return promo, bal


reward_service = RewardService()
