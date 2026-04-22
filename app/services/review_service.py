"""Review service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.schemas.review import EligibilityResponse, ReviewCreate, ReviewUpdate
from app.repositories.review_repository import review_repository
from app.services.points_service import points_service


class ReviewService:
    """Logic nghiệp vụ cho Review."""

    def __init__(self):
        self.repository = review_repository

    async def create_review(
        self, db: AsyncSession, review_in: ReviewCreate, user_id: int
    ) -> Review:
        """Tạo đánh giá: đã mua, đã giao (COMPLETED/DELIVERED) trong 30 ngày; 1 lần/sách (bản còn hiệu lực)."""
        existing = await self.repository.get_by_user_and_book(
            db, user_id, review_in.book_id
        )
        if existing:
            raise ValueError("You have already reviewed this book")
        can_create, _already, _last = await self.repository.get_user_book_eligibility(
            db, user_id, review_in.book_id, window_days=30
        )
        if not can_create:
            raise ValueError("Not eligible to review this book")
        data = review_in.model_dump()
        data["user_id"] = user_id
        data["create_at"] = datetime.utcnow()
        review = await self.repository.create(db, ReviewCreate(**data))
        try:
            await points_service.award_for_new_review(db, user_id, review.id)
        except Exception:
            # Không làm hỏng luồng review nếu cộng điểm lỗi (log server)
            import logging

            logging.exception("award_for_new_review failed")
        try:
            from app.services.notification_service import notification_service

            await notification_service.notify_admins_new_review(
                db, review_in.book_id, review.id
            )
        except Exception:
            import logging

            logging.exception("notify_admins_new_review failed")
        return review

    async def get_by_book(
        self, db: AsyncSession, book_id: int, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        return await self.repository.get_by_book(db, book_id, skip, limit)

    async def get_avg_rate(self, db: AsyncSession, book_id: int) -> Optional[float]:
        return await self.repository.get_avg_rate(db, book_id)

    async def count_by_book(self, db: AsyncSession, book_id: int) -> int:
        return await self.repository.count_by_book(db, book_id)

    async def get_eligibility(
        self, db: AsyncSession, user_id: int, book_id: int, window_days: int = 30
    ) -> EligibilityResponse:
        can_create, already, last_at = await self.repository.get_user_book_eligibility(
            db, user_id, book_id, window_days=window_days
        )
        return EligibilityResponse(
            eligible=can_create,
            already_reviewed=already,
            last_delivered_at=last_at,
        )

    async def get_my_review_by_book(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> Optional[Review]:
        return await self.repository.get_by_user_and_book(db, user_id, book_id)

    async def update_review(
        self, db: AsyncSession, review_id: int, user_id: int, review_in: ReviewUpdate
    ) -> Optional[Review]:
        review = await self.repository.get(db, review_id)
        if not review or review.user_id != user_id or review.deleted_at is not None:
            return None
        return await self.repository.update(db, review, review_in)

    async def delete_review(
        self, db: AsyncSession, review_id: int, user_id: int
    ) -> bool:
        review = await self.repository.get(db, review_id)
        if not review or review.user_id != user_id:
            return False
        review.deleted_at = datetime.utcnow()
        await db.flush()
        return True


review_service = ReviewService()
