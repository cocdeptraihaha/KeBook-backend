"""Book endpoints - sách."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.book import (
    Book as BookSchema,
    BookCreate,
    BookCreateWithDetail,
    BookUpdate,
    BookWithDetailOut,
)
from app.repositories.book_repository import book_repository
from app.repositories.book_view_repository import book_view_repository
from app.services.book_service import book_service

router = APIRouter()


@router.get("/", response_model=Page[BookSchema])
async def list_books(
    q: str | None = Query(None, description="Search by title, author"),
    category_id: int | None = Query(None, description="Filter books by category_id"),
    db: AsyncSession = Depends(get_db),
):
    """List books with pagination (public - no auth required)."""
    stmt = book_service.build_list_query(q=q, category_id=category_id)
    return await apaginate(db, stmt)


@router.get("/top-selling", response_model=list[BookSchema])
async def top_selling_books(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Top N best-selling books by quantity."""
    return await book_service.get_top_selling(db, limit)


@router.get("/top-discounted", response_model=list[BookSchema])
async def top_discounted_books(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Top N books by biggest active discount amount."""
    return await book_service.get_top_discounted(db, limit)


@router.get("/{book_id}/similar", response_model=list[BookSchema])
async def similar_books(
    book_id: int,
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Sách cùng thể loại (gợi ý tương tự)."""
    book = await book_service.repository.get(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await book_repository.get_similar_books(db, book_id, limit=limit)


@router.post("/{book_id}/view", status_code=status.HTTP_204_NO_CONTENT)
async def record_book_view(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ghi nhận user đã xem sách (để đã xem + đếm lượt xem)."""
    book = await book_service.repository.get(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    await book_view_repository.record(db, current_user.id, book_id)
    return None


@router.get("/{book_id}", response_model=BookWithDetailOut)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Book detail + thống kê (public)."""
    book = await book_service.repository.get_with_detail(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    # Materialize quan hệ trong phiên async (tránh lazy-load khi serialize response)
    _ = list(book.discounts or [])
    _ = book.book_detail
    bc, rc, vc = await book_repository.get_book_stats(db, book_id)
    out = BookWithDetailOut.model_validate(book, from_attributes=True)
    return out.model_copy(
        update={"buyer_count": bc, "review_count": rc, "view_count": vc}
    )


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate | BookCreateWithDetail,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create new book (admin only). Can include nested book_detail to create both in one call."""
    detail_in = getattr(book_in, "book_detail", None)
    data = {k: v for k, v in book_in.model_dump().items() if k != "book_detail"}
    book_data = BookCreate(**data)
    book = await book_service.create_book(db, book_data, detail_in=detail_in)
    full = await book_service.repository.get_with_detail(db, book.id)
    if full:
        _ = list(full.discounts or [])
        _ = full.book_detail
        return full
    _ = list(book.discounts or [])
    return book


@router.patch("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update book (admin only)."""
    book = await book_service.repository.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book = await book_service.repository.update(db, book, book_in)
    full = await book_service.repository.get_with_detail(db, book.id)
    if full:
        _ = list(full.discounts or [])
        _ = full.book_detail
        return full
    _ = list(book.discounts or [])
    return book
