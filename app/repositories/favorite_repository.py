"""Favorite (yêu thích) repository."""
from typing import List, Optional, Set
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite
from app.models.book import Book


class FavoriteRepository:
    async def add(self, db: AsyncSession, user_id: int, book_id: int) -> Favorite:
        existing = await self.get_one(db, user_id, book_id)
        if existing:
            return existing
        row = Favorite(user_id=user_id, book_id=book_id)
        try:
            async with db.begin_nested():
                db.add(row)
                await db.flush()
        except IntegrityError:
            pass
        out = await self.get_one(db, user_id, book_id)
        if out:
            return out
        raise RuntimeError("favorite insert failed unexpectedly")

    async def remove(self, db: AsyncSession, user_id: int, book_id: int) -> bool:
        r = await db.execute(
            delete(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.book_id == book_id,
            )
        )
        await db.flush()
        return (r.rowcount or 0) > 0

    async def get_one(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> Optional[Favorite]:
        res = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.book_id == book_id,
            )
        )
        return res.scalars().first()

    async def list_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[Book]:
        r = await db.execute(
            select(Book)
            .join(Favorite, Favorite.book_id == Book.id)
            .where(Favorite.user_id == user_id, Book.deleted_at.is_(None))
            .options(
                selectinload(Book.book_detail),
                selectinload(Book.discounts),
                selectinload(Book.images),
            )
            .order_by(Favorite.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(r.scalars().all())

    async def check_map(
        self, db: AsyncSession, user_id: int, book_ids: List[int]
    ) -> dict[int, bool]:
        if not book_ids:
            return {}
        r = await db.execute(
            select(Favorite.book_id).where(
                Favorite.user_id == user_id,
                Favorite.book_id.in_(book_ids),
            )
        )
        have: Set[int] = {row[0] for row in r.all()}
        return {bid: bid in have for bid in book_ids}


favorite_repository = FavoriteRepository()
