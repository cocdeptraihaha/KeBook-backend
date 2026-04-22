"""Promotion service."""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

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
        discount = 0
        if promo.discount_percent:
            discount = order_total * (promo.discount_percent / 100)
        if promo.max_discount and discount > promo.max_discount:
            discount = promo.max_discount
        return promo, discount, None

    async def get_multi_active(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Promotion]:
        return await self.repository.get_multi_active(db, skip, limit)


promotion_service = PromotionService()
