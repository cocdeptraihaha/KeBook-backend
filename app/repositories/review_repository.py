"""Review repository."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory, OrderHistoryStatus
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
                Review.deleted_at.is_(None),  # noqa: E712
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
                Review.deleted_at.is_(None),  # noqa: E712
            )
        )
        return result.scalars().first()

    async def get_avg_rate(self, db: AsyncSession, book_id: int) -> Optional[float]:
        """Điểm trung bình của sách."""
        result = await db.execute(
            select(func.avg(Review.rate)).where(
                Review.book_id == book_id,
                Review.deleted_at.is_(None),  # noqa: E712
            )
        )
        return result.scalar()

    async def count_by_book(
        self, db: AsyncSession, book_id: int
    ) -> int:
        """Số lượng review còn hiệu lực của sách."""
        result = await db.execute(
            select(func.count(Review.id)).where(
                Review.book_id == book_id,
                Review.deleted_at.is_(None),  # noqa: E712
            )
        )
        return int(result.scalar() or 0)

    @staticmethod
    def _naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    async def _order_delivered_at(
        self, db: AsyncSession, order: Order
    ) -> Optional[datetime]:
        """Thời điểm giao/hoàn tất: max history DELIVERED|COMPLETED hoặc order_date."""
        r = await db.execute(
            select(func.max(OrderStatusHistory.status_change_date)).where(
                OrderStatusHistory.order_id == order.id,
                OrderStatusHistory.e_order_history.in_(
                    (OrderHistoryStatus.DELIVERED, OrderHistoryStatus.COMPLETED)
                ),
            )
        )
        at = r.scalar()
        if at is not None:
            return at
        return order.order_date

    async def get_last_delivered_at_for_user_book(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> Optional[datetime]:
        """
        Mới nhất (max) thời điểm 'đã giao' trong số đơn DELIVERED/COMPLETED
        của user + book (order_item).
        """
        r_orders = await db.execute(
            select(Order)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .where(
                Order.user_id == user_id,
                OrderItem.book_id == book_id,
                OrderItem.deleted_at.is_(None),  # noqa: E712
                Order.deleted_at.is_(None),  # noqa: E712
                Order.status.in_(
                    (OrderStatus.DELIVERED, OrderStatus.COMPLETED)
                ),
            )
        )
        orders = list(r_orders.scalars().all())
        if not orders:
            return None
        best: Optional[datetime] = None
        for o in orders:
            t = await self._order_delivered_at(db, o)
            if t is not None and (best is None or t > best):
                best = t
        return best

    def purchased_within_review_window(
        self,
        last_delivered_at: Optional[datetime],
        window_days: int = 30,
    ) -> bool:
        if last_delivered_at is None:
            return False
        last = self._naive_utc(last_delivered_at)
        if last is None:
            return False
        now = datetime.now(timezone.utc)
        return (now - last) <= timedelta(days=window_days)

    async def get_user_book_eligibility(
        self,
        db: AsyncSession,
        user_id: int,
        book_id: int,
        window_days: int = 30,
    ) -> Tuple[bool, bool, Optional[datetime]]:
        """
        (eligible, already_reviewed, last_delivered_at)
        - eligible: trong cửa sổ window_days sau khi giao và chưa có review còn hiệu lực.
        - already_reviewed: user đã có bản ghi review chưa xóa mềm.
        - last_delivered_at: thời điểm giao mới nhất tính được (display).
        """
        existing = await self.get_by_user_and_book(db, user_id, book_id)
        already = existing is not None
        last_at = await self.get_last_delivered_at_for_user_book(db, user_id, book_id)
        in_window = self.purchased_within_review_window(
            last_at, window_days=window_days
        )
        can_create = in_window and not already
        return can_create, already, last_at

    async def get_by_user_and_book_any(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> Optional[Review]:
        """
        Có cả bản ghi bị xóa mềm (cho tra cứu, ít dùng).
        """
        result = await db.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.book_id == book_id,
            )
        )
        return result.scalars().first()


review_repository = ReviewRepository(Review)
