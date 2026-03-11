"""Book repository."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.book_detail import BookDetail
from app.schemas.book import BookCreate, BookUpdate, BookDetailCreate, BookDetailUpdate
from app.repositories.base_repository import BaseRepository


class BookRepository(BaseRepository[Book, BookCreate, BookUpdate]):
    """Repository cho Book."""

    async def get_with_detail(self, db: AsyncSession, id: int) -> Optional[Book]:
        """Lấy book kèm book_detail."""
        result = await db.execute(
            select(Book)
            .where(Book.id == id)
            .options(selectinload(Book.book_detail), selectinload(Book.discounts))
        )
        return result.scalars().first()

    async def get_multi_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Book]:
        """Lấy danh sách book chưa xóa."""
        result = await db.execute(
            select(Book)
            .where(Book.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        db: AsyncSession,
        q: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Book]:
        """Tìm sách theo title, author."""
        stmt = select(Book).where(Book.deleted_at.is_(None))
        if q:
            stmt = stmt.where(
                (Book.title.like(f"%{q}%")) | (Book.author.like(f"%{q}%"))
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


class BookDetailRepository(BaseRepository[BookDetail, BookDetailCreate, BookDetailUpdate]):
    """Repository cho BookDetail."""

    pass


book_repository = BookRepository(Book)
book_detail_repository = BookDetailRepository(BookDetail)
