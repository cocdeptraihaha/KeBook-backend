"""Promotion repository."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotion import Promotion
from app.schemas.promotion import PromotionCreate, PromotionUpdate
from app.repositories.base_repository import BaseRepository


class PromotionRepository(BaseRepository[Promotion, PromotionCreate, PromotionUpdate]):
    """Repository cho Promotion."""

    async def get_by_code(
        self, db: AsyncSession, code: str
    ) -> Optional[Promotion]:
        """Lấy promotion theo mã (chưa xóa, còn hạn)."""
        now = datetime.utcnow()
        result = await db.execute(
            select(Promotion).where(
                Promotion.code == code.strip().upper(),
                Promotion.deleted_at.is_(None),  # noqa: E712
                (Promotion.start_date.is_(None)) | (Promotion.start_date <= now),
                (Promotion.end_date.is_(None)) | (Promotion.end_date >= now),
            )
        )
        return result.scalars().first()

    async def get_multi_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Promotion]:
        """Danh sách promotion chưa xóa."""
        result = await db.execute(
            select(Promotion)
            .where(Promotion.deleted_at.is_(None))  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


promotion_repository = PromotionRepository(Promotion)
