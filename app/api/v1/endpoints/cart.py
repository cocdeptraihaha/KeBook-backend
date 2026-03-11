"""Cart endpoints - giỏ hàng."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.cart import Cart as CartModel
from app.models.book import Book as BookModel
from app.models.book_detail import BookDetail as BookDetailModel
from app.models.book_discount import BookDiscount
from app.models.book_book_discount import BookBookDiscount
from app.schemas.cart import Cart, CartCreate, CartUpdate, CartWithBook, CartItemSummary
from app.services.cart_service import cart_service

router = APIRouter()


@router.get("/", response_model=list[Cart])
async def get_my_cart(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get cart of logged-in user."""
    return await cart_service.get_user_cart(db, current_user.id, skip, limit)


@router.get("/summary", response_model=list[CartItemSummary])
async def get_my_cart_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get cart of logged-in user with book basic info and discount-aware pricing."""
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
            CartModel,
            BookModel.title,
            BookModel.selling_price,
            BookModel.stock_quantity,
            BookDetailModel.image_url,
            func.coalesce(disc_subq.c.best_discount, 0.0).label("best_discount"),
        )
        .join(BookModel, CartModel.book_id == BookModel.id)
        .join(
            BookDetailModel,
            BookModel.book_detail_id == BookDetailModel.id,
            isouter=True,
        )
        .join(disc_subq, BookModel.id == disc_subq.c.book_id, isouter=True)
        .where(CartModel.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    rows = result.all()
    summaries: list[CartItemSummary] = []
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


@router.post("/", response_model=Cart, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_in: CartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add book to cart."""
    return await cart_service.add_to_cart(db, current_user.id, cart_in)


@router.patch("/{cart_id}", response_model=Cart)
async def update_cart_item(
    cart_id: int,
    cart_in: CartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update quantity in cart."""
    if cart_in.quantity is None:
        raise HTTPException(status_code=400, detail="Quantity is required")
    cart = await cart_service.update_quantity(
        db, cart_id, current_user.id, cart_in.quantity
    )
    if not cart:
        raise HTTPException(status_code=404, detail="Item not found")
    return cart


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    cart_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove item from cart."""
    ok = await cart_service.remove_from_cart(db, cart_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
