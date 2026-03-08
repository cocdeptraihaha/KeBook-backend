"""Book endpoints - sách."""
from sqlalchemy import select, or_, func
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas.book import Book as BookSchema, BookCreate, BookUpdate, BookWithDetail
from app.services.book_service import book_service

router = APIRouter()


@router.get("/", response_model=Page[BookSchema])
async def list_books(
    q: str | None = Query(None, description="Search by title, author"),
    db: AsyncSession = Depends(get_db),
):
    """List books with pagination (public - no auth required)."""
    stmt = (
        select(Book)
        .where(Book.is_deleted == False)  # noqa: E712
        .order_by(Book.id)
    )
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Book.title).like(pattern),
                func.lower(Book.author).like(pattern),
            )
        )
    return await apaginate(db, stmt)


@router.get("/{book_id}", response_model=BookSchema)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Book detail (public)."""
    book = await book_service.repository.get_with_detail(db, book_id)
    if not book or book.is_deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create new book (admin only)."""
    book = await book_service.create_book(db, book_in)
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
    return book
