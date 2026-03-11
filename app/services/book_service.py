"""Book service."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.book_detail import BookDetail
from app.schemas.book import BookCreate, BookUpdate, BookDetailCreate
from app.repositories.book_repository import book_repository, book_detail_repository


class BookService:
    """Logic nghiệp vụ cho Book."""

    def __init__(self):
        self.repository = book_repository
        self.detail_repository = book_detail_repository

    async def create_book(
        self, db: AsyncSession, book_in: BookCreate, detail_in: Optional[BookDetailCreate] = None
    ) -> Book:
        """Tạo sách mới, có thể kèm book_detail."""
        if detail_in:
            detail = await self.detail_repository.create(db, detail_in)
            await db.flush()
            data = book_in.model_dump()
            data["book_detail_id"] = detail.id
        else:
            data = book_in.model_dump()
        book = await self.repository.create(db, BookCreate(**data))
        return book

    async def get_multi_active(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Book]:
        return await self.repository.get_multi_active(db, skip, limit)

    async def search(
        self, db: AsyncSession, q: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Book]:
        return await self.repository.search(db, q, skip, limit)

    def build_list_query(self, q: Optional[str] = None, category_id: Optional[int] = None):
        """Delegate to repository for paginated listing."""
        return self.repository.build_list_query(q=q, category_id=category_id)

    async def get_top_selling(self, db: AsyncSession, limit: int = 10) -> List[Book]:
        return await self.repository.get_top_selling(db, limit)

    async def get_top_discounted(self, db: AsyncSession, limit: int = 20) -> List[Book]:
        return await self.repository.get_top_discounted(db, limit)


book_service = BookService()
