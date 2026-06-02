"""Promotion service."""
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order_promotion import OrderPromotion
from app.models.promotion import Promotion
from app.schemas.promotion import PromotionCreate, PromotionUpdate
from app.repositories.promotion_repository import promotion_repository


class PromotionService:
    """Logic nghiệp vụ cho Promotion."""

    def __init__(self):
        self.repository = promotion_repository

    async def validate_code(
        self,
        db: AsyncSession,
        code: str,
        order_total: float,
        user_id: Optional[int] = None,
    ) -> Tuple[Optional[Promotion], float, Optional[str]]:
        """
        Validate mã khuyến mãi. Return (promotion, discount_amount, error).
        Nếu promotion.owner_user_id được set, chỉ user đó mới dùng được (mã đổi điểm).
        """
        promo = await self.repository.get_by_code(db, code)
        if not promo:
            return None, 0, "Invalid or expired promotion code"
        if getattr(promo, "owner_user_id", None) is not None:
            if user_id is None or int(user_id) != int(promo.owner_user_id):
                return None, 0, "Chỉ chủ tài khoản mới được dùng mã này"
        min_amt = getattr(promo, "min_order_amount", None) or 0
        if min_amt > 0 and float(order_total) < float(min_amt):
            return None, 0, f"Đơn chưa đạt giá trị tối thiểu {float(min_amt):,.0f}đ để dùng mã này"
        usage_limit = getattr(promo, "usage_limit", None)
        if usage_limit is not None and int(usage_limit) > 0:
            used = int(getattr(promo, "used_count", 0) or 0)
            if used >= int(usage_limit):
                return None, 0, "Mã khuyến mãi đã hết lượt sử dụng"
        discount = 0
        fixed_amount = getattr(promo, "discount_amount", None)
        if fixed_amount:
            discount = min(float(order_total), float(fixed_amount))
        if promo.discount_percent:
            discount = order_total * (promo.discount_percent / 100)
        if promo.max_discount and discount > promo.max_discount:
            discount = promo.max_discount
        return promo, discount, None

    async def get_multi_active(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Promotion]:
        return await self.repository.get_multi_active(db, skip, limit)

    async def get_usage_stats(self, db: AsyncSession, promotion_id: int) -> dict:
        r = await db.execute(
            select(
                func.count(OrderPromotion.id),
                func.coalesce(func.sum(OrderPromotion.discount_amount), 0.0),
            ).where(OrderPromotion.promotion_id == promotion_id)
        )
        row = r.one()
        return {
            "promotion_id": promotion_id,
            "usage_count": int(row[0] or 0),
            "total_discount": float(row[1] or 0),
        }

    async def issue_personal_copy(
        self, db: AsyncSession, user_id: int, template_promotion_id: int
    ) -> Promotion:
        tpl = await self.repository.get(db, template_promotion_id)
        if not tpl:
            raise ValueError("Promotion mẫu không tồn tại")
        now = datetime.utcnow()
        end = tpl.end_date
        if end is None or end <= now:
            end = now + timedelta(days=30)
        code = f"ISS{user_id}{secrets.token_hex(3).upper()}"
        name = f"{tpl.name or 'Voucher'} (cấp admin)"
        new = Promotion(
            owner_user_id=user_id,
            code=code,
            name=name,
            discount_percent=tpl.discount_percent,
            discount_amount=getattr(tpl, "discount_amount", None),
            free_shipping=bool(getattr(tpl, "free_shipping", False)),
            max_discount=tpl.max_discount,
            min_order_amount=getattr(tpl, "min_order_amount", None),
            usage_limit=1,
            used_count=0,
            start_date=now,
            end_date=end,
            deleted_at=None,
        )
        db.add(new)
        await db.flush()
        await db.refresh(new)
        return new


promotion_service = PromotionService()
