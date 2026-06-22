"""Book service."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.book_category import BookCategory
from app.models.book_detail import BookDetail
from app.models.category import Category
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

    def build_list_query(
        self,
        q: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        publisher: Optional[str] = None,
    ):
        """Delegate to repository for paginated listing with advanced filters."""
        return self.repository.build_list_query(
            q=q,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            publisher=publisher,
        )

    async def get_top_selling(self, db: AsyncSession, limit: int = 10) -> List[Book]:
        return await self.repository.get_top_selling(db, limit)

    async def get_top_discounted(self, db: AsyncSession, limit: int = 20) -> List[Book]:
        return await self.repository.get_top_discounted(db, limit)

    def build_admin_list_query(
        self,
        *,
        include_deleted: bool = False,
        status: Optional[str] = None,
        q: Optional[str] = None,
        category_id: Optional[int] = None,
        sort: str = "id",
        order: str = "desc",
    ):
        return self.repository.build_admin_list_query(
            include_deleted=include_deleted,
            status=status,
            q=q,
            category_id=category_id,
            sort=sort,
            order=order,
        )

    async def list_low_stock(
        self, db: AsyncSession, *, threshold: int = 5, limit: int = 50
    ) -> List[Book]:
        return await self.repository.list_low_stock(db, threshold=threshold, limit=limit)

    async def soft_delete_book(self, db: AsyncSession, book_id: int) -> Optional[Book]:
        book = await self.repository.get(db, book_id)
        if not book:
            return None
        book.deleted_at = datetime.utcnow()
        await db.flush()
        await db.refresh(book)
        return book

    async def restore_book(self, db: AsyncSession, book_id: int) -> Optional[Book]:
        book = await self.repository.get(db, book_id)
        if not book:
            return None
        book.deleted_at = None
        await db.flush()
        await db.refresh(book)
        return book

    async def replace_book_categories(
        self, db: AsyncSession, book_id: int, category_ids: List[int]
    ) -> Book:
        book = await self.repository.get(db, book_id)
        if not book:
            raise ValueError("Book not found")
        if category_ids:
            r = await db.execute(
                select(Category).where(
                    Category.id.in_(category_ids),
                    Category.deleted_at.is_(None),
                )
            )
            found = {c.id for c in r.scalars().all()}
            missing = set(category_ids) - found
            if missing:
                raise ValueError(f"Category không tồn tại: {sorted(missing)}")
        await db.execute(delete(BookCategory).where(BookCategory.book_id == book_id))
        for cid in category_ids:
            db.add(BookCategory(book_id=book_id, category_id=cid))
        await db.flush()
        full = await self.repository.get_with_detail(db, book_id)
        if not full:
            raise ValueError("Book not found")
        return full


book_service = BookService()
