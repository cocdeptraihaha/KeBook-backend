"""Book view tracking."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book_view import BookView


class BookViewRepository:
    async def record(self, db: AsyncSession, user_id: int, book_id: int) -> BookView:
        row = BookView(user_id=user_id, book_id=book_id)
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row


book_view_repository = BookViewRepository()
