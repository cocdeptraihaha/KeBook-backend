"""Cart repository."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.schemas.cart import CartCreate, CartUpdate
from app.repositories.base_repository import BaseRepository


class CartRepository(BaseRepository[Cart, CartCreate, CartUpdate]):
    """Repository cho Cart."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Cart]:
        """Lấy giỏ hàng của user (chưa xóa)."""
        result = await db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.book))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user_and_book(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> Optional[Cart]:
        """Lấy item giỏ hàng theo user và book."""
        result = await db.execute(
            select(Cart).where(
                Cart.user_id == user_id,
                Cart.book_id == book_id,
            )
        )
        return result.scalars().first()


cart_repository = CartRepository(Cart)
