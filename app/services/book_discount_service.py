"""CRUD giảm giá theo sách (BookDiscount) — admin."""
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.book_discount import BookDiscount


def _validate_discount_payload(
    discount_amount: Optional[float],
    discount_percent: Optional[float],
) -> None:
    has_amt = discount_amount is not None and discount_amount > 0
    has_pct = discount_percent is not None and discount_percent > 0
    if not has_amt and not has_pct:
        raise ValueError("Cần discount_amount > 0 hoặc discount_percent > 0")


class BookDiscountService:
    async def list_all(
        self,
        db: AsyncSession,
        *,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BookDiscount]:
        stmt = select(BookDiscount).options(selectinload(BookDiscount.books))
        now = datetime.utcnow()
        if active_only:
            stmt = stmt.where(
                (BookDiscount.start_date.is_(None)) | (BookDiscount.start_date <= now),
                (BookDiscount.end_date.is_(None)) | (BookDiscount.end_date >= now),
            )
        stmt = stmt.order_by(BookDiscount.id.desc()).offset(skip).limit(limit)
        r = await db.execute(stmt)
        return list(r.scalars().unique().all())

    async def get(self, db: AsyncSession, discount_id: int) -> Optional[BookDiscount]:
        r = await db.execute(
            select(BookDiscount)
            .where(BookDiscount.id == discount_id)
            .options(selectinload(BookDiscount.books))
        )
        return r.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        *,
        discount_amount: Optional[float],
        discount_percent: Optional[float],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        book_ids: List[int],
    ) -> BookDiscount:
        _validate_discount_payload(discount_amount, discount_percent)
        if not book_ids:
            raise ValueError("book_ids không được rỗng")

        r = await db.execute(select(Book).where(Book.id.in_(book_ids), Book.deleted_at.is_(None)))
        books = list(r.scalars().all())
        if len(books) != len(set(book_ids)):
            raise ValueError("Một hoặc nhiều book_id không tồn tại hoặc đã xóa")

        d = BookDiscount(
            discount_amount=discount_amount,
            discount_percent=discount_percent,
            start_date=start_date,
            end_date=end_date,
        )
        d.books = books
        db.add(d)
        await db.flush()
        await db.refresh(d)
        return await self.get(db, d.id) or d

    async def update(self, db: AsyncSession, discount_id: int, data: dict[str, Any]) -> Optional[BookDiscount]:
        d = await self.get(db, discount_id)
        if not d:
            return None

        if "discount_amount" in data:
            d.discount_amount = data["discount_amount"]
        if "discount_percent" in data:
            d.discount_percent = data["discount_percent"]
        if "start_date" in data:
            d.start_date = data["start_date"]
        if "end_date" in data:
            d.end_date = data["end_date"]

        if "book_ids" in data:
            book_ids = data["book_ids"]
            if not book_ids:
                raise ValueError("book_ids không được rỗng")
            r = await db.execute(select(Book).where(Book.id.in_(book_ids), Book.deleted_at.is_(None)))
            books = list(r.scalars().all())
            if len(books) != len(set(book_ids)):
                raise ValueError("Một hoặc nhiều book_id không tồn tại hoặc đã xóa")
            d.books = books

        _validate_discount_payload(d.discount_amount, d.discount_percent)
        await db.flush()
        return await self.get(db, discount_id)

    async def delete(self, db: AsyncSession, discount_id: int) -> bool:
        d = await self.get(db, discount_id)
        if not d:
            return False
        d.books.clear()
        await db.flush()
        await db.delete(d)
        await db.flush()
        return True


book_discount_service = BookDiscountService()
