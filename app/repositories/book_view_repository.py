"""Book view tracking."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book_view import BookView


class BookViewRepository:
    async def get_latest_view_at(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> Optional[datetime]:
        r = await db.execute(
            select(BookView.viewed_at)
            .where(BookView.user_id == user_id, BookView.book_id == book_id)
            .order_by(desc(BookView.viewed_at))
            .limit(1)
        )
        row = r.scalar_one_or_none()
        return row

    async def record(self, db: AsyncSession, user_id: int, book_id: int) -> BookView:
        row = BookView(user_id=user_id, book_id=book_id)
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    async def record_if_debounced(
        self,
        db: AsyncSession,
        user_id: int,
        book_id: int,
        *,
        debounce_minutes: int,
    ) -> Tuple[bool, Optional[BookView]]:
        """
        Ghi view mới nếu đủ thời gian kể từ lần gần nhất.
        Returns (did_record, row_or_none).
        """
        last = await self.get_latest_view_at(db, user_id, book_id)
        now = datetime.now(timezone.utc)
        if last is not None:
            la = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
            if (now - la) < timedelta(minutes=debounce_minutes):
                return False, None
        row = await self.record(db, user_id, book_id)
        return True, row


book_view_repository = BookViewRepository()
