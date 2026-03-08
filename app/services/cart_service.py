"""Cart service."""
from datetime import date
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.models.book import Book
from app.schemas.cart import CartCreate, CartUpdate
from app.repositories.cart_repository import cart_repository


class CartService:
    """Logic nghiệp vụ cho Cart."""

    def __init__(self):
        self.repository = cart_repository

    async def add_to_cart(
        self, db: AsyncSession, user_id: int, cart_in: CartCreate
    ) -> Cart:
        """Thêm sách vào giỏ (hoặc cập nhật quantity nếu đã có)."""
        existing = await self.repository.get_by_user_and_book(
            db, user_id, cart_in.book_id
        )
        if existing:
            existing.quantity = (existing.quantity or 0) + cart_in.quantity
            existing.update_at = date.today()
            await db.flush()
            await db.refresh(existing)
            return existing
        cart = await self.repository.create(
            db,
            CartCreate(
                book_id=cart_in.book_id,
                quantity=cart_in.quantity,
                user_id=user_id,
            ),
        )
        cart.create_at = date.today()
        cart.update_at = date.today()
        await db.flush()
        return cart

    async def get_user_cart(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Cart]:
        return await self.repository.get_by_user(db, user_id, skip, limit)

    async def update_quantity(
        self, db: AsyncSession, cart_id: int, user_id: int, quantity: int
    ) -> Cart | None:
        cart = await self.repository.get(db, cart_id)
        if not cart or cart.user_id != user_id:
            return None
        cart.quantity = quantity
        cart.update_at = date.today()
        await db.flush()
        await db.refresh(cart)
        return cart

    async def remove_from_cart(
        self, db: AsyncSession, cart_id: int, user_id: int
    ) -> bool:
        """Xóa item khỏi giỏ (hard delete)."""
        cart = await self.repository.get(db, cart_id)
        if not cart or cart.user_id != user_id:
            return False
        await db.delete(cart)
        await db.flush()
        return True


cart_service = CartService()
