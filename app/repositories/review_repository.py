"""Review repository."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository[Review, ReviewCreate, ReviewUpdate]):
    """Repository cho Review."""

    async def get_by_book(
        self,
        db: AsyncSession,
        book_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Review]:
        """Lấy đánh giá theo sách (chưa xóa)."""
        result = await db.execute(
            select(Review)
            .where(
                Review.book_id == book_id,
                Review.is_deleted == False,  # noqa: E712
            )
            .options(selectinload(Review.user))
            .order_by(Review.create_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user_and_book(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> Optional[Review]:
        """Kiểm tra user đã đánh giá sách chưa."""
        result = await db.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.book_id == book_id,
                Review.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalars().first()

    async def get_avg_rate(self, db: AsyncSession, book_id: int) -> Optional[float]:
        """Điểm trung bình của sách."""
        result = await db.execute(
            select(func.avg(Review.rate)).where(
                Review.book_id == book_id,
                Review.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar()


review_repository = ReviewRepository(Review)
