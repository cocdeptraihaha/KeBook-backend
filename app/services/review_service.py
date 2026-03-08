"""Review service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.repositories.review_repository import review_repository


class ReviewService:
    """Logic nghiệp vụ cho Review."""

    def __init__(self):
        self.repository = review_repository

    async def create_review(
        self, db: AsyncSession, review_in: ReviewCreate, user_id: int
    ) -> Review:
        """Tạo đánh giá (1 user chỉ đánh giá 1 lần/sách)."""
        existing = await self.repository.get_by_user_and_book(
            db, user_id, review_in.book_id
        )
        if existing:
            raise ValueError("You have already reviewed this book")
        data = review_in.model_dump()
        data["user_id"] = user_id
        data["create_at"] = datetime.utcnow()
        review = await self.repository.create(db, ReviewCreate(**data))
        return review

    async def get_by_book(
        self, db: AsyncSession, book_id: int, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        return await self.repository.get_by_book(db, book_id, skip, limit)

    async def get_avg_rate(self, db: AsyncSession, book_id: int) -> Optional[float]:
        return await self.repository.get_avg_rate(db, book_id)

    async def update_review(
        self, db: AsyncSession, review_id: int, user_id: int, review_in: ReviewUpdate
    ) -> Optional[Review]:
        review = await self.repository.get(db, review_id)
        if not review or review.user_id != user_id or review.is_deleted:
            return None
        return await self.repository.update(db, review, review_in)

    async def delete_review(
        self, db: AsyncSession, review_id: int, user_id: int
    ) -> bool:
        review = await self.repository.get(db, review_id)
        if not review or review.user_id != user_id:
            return False
        review.is_deleted = True
        review.deleted_at = datetime.utcnow()
        await db.flush()
        return True


review_service = ReviewService()
