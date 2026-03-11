"""Cart service."""
from datetime import date
from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.models.book import Book as BookModel
from app.models.book_detail import BookDetail as BookDetailModel
from app.models.book_discount import BookDiscount
from app.models.book_book_discount import BookBookDiscount
from app.schemas.cart import CartCreate, CartUpdate, CartItemSummary
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

    async def get_user_cart_summary(
        self, db: AsyncSession, user_id: int
    ) -> List[CartItemSummary]:
        """Get cart with book info and discount-aware pricing."""
        now = func.now()

        percent_amount = (
            func.coalesce(BookModel.selling_price, 0)
            * func.coalesce(BookDiscount.discount_percent, 0)
            / 100.0
        )
        amount_expr = func.greatest(
            func.coalesce(BookDiscount.discount_amount, 0),
            func.coalesce(percent_amount, 0),
        )
        disc_subq = (
            select(
                BookBookDiscount.book_id.label("book_id"),
                func.max(amount_expr).label("best_discount"),
            )
            .join(BookDiscount, BookDiscount.id == BookBookDiscount.discount_id)
            .join(BookModel, BookModel.id == BookBookDiscount.book_id)
            .where(
                BookModel.deleted_at.is_(None),
                func.coalesce(BookDiscount.start_date, now) <= now,
                func.coalesce(BookDiscount.end_date, now) >= now,
            )
            .group_by(BookBookDiscount.book_id)
            .subquery()
        )
        stmt = (
            select(
                Cart,
                BookModel.title,
                BookModel.selling_price,
                BookModel.stock_quantity,
                BookDetailModel.image_url,
                func.coalesce(disc_subq.c.best_discount, 0.0).label("best_discount"),
            )
            .join(BookModel, Cart.book_id == BookModel.id)
            .join(
                BookDetailModel,
                BookModel.book_detail_id == BookDetailModel.id,
                isouter=True,
            )
            .join(disc_subq, BookModel.id == disc_subq.c.book_id, isouter=True)
            .where(Cart.user_id == user_id)
        )
        result = await db.execute(stmt)
        rows = result.all()
        summaries: List[CartItemSummary] = []
        for cart_row, title, selling_price, stock_quantity, image_url, best_discount in rows:
            selling_price = selling_price or 0.0
            best_discount = best_discount or 0.0
            final_price = max(0.0, selling_price - best_discount)
            summaries.append(
                CartItemSummary(
                    id=cart_row.id,
                    quantity=cart_row.quantity or 0,
                    book_id=cart_row.book_id,
                    title=title,
                    price=final_price,
                    original_price=selling_price,
                    image_url=image_url,
                    stock_quantity=stock_quantity,
                )
            )
        return summaries

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
