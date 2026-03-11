"""Book endpoints - sách."""
from sqlalchemy import select, or_, func, exists
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.book import Book
from app.models.book_category import BookCategory
from app.models.book_detail import BookDetail
from app.models.category import Category
from app.models.user import User
from app.schemas.book import Book as BookSchema, BookCreate, BookCreateWithDetail, BookUpdate, BookWithDetail
from app.services.book_service import book_service

router = APIRouter()


@router.get("/", response_model=Page[BookSchema])
async def list_books(
    q: str | None = Query(None, description="Search by title, author"),
    category_id: int | None = Query(None, description="Filter books by category_id"),
    db: AsyncSession = Depends(get_db),
):
    """List books with pagination (public - no auth required)."""
    stmt = select(Book).join(BookDetail, Book.book_detail_id == BookDetail.id, isouter=True)

    # Filter by category tree (parent -> all descendants + itself)
    if category_id is not None:
        cat_tree = (
            select(Category.id)
            .where(Category.id == category_id)
            .cte(name="cat_tree", recursive=True)
        )
        cat_tree = cat_tree.union_all(
            select(Category.id)
            .join(cat_tree, Category.parent_id == cat_tree.c.id)
        )

        stmt = stmt.where(
            exists(
                select(1)
                .select_from(BookCategory)
                .where(BookCategory.book_id == Book.id)
                .where(BookCategory.category_id.in_(select(cat_tree.c.id)))
            )
        )
    else:
        stmt = stmt.join(BookCategory, BookCategory.book_id == Book.id, isouter=True)

    stmt = stmt.where(Book.deleted_at.is_(None)).order_by(Book.id)  # noqa: E712
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Book.title).like(pattern),
                func.lower(Book.author).like(pattern),
                func.lower(BookDetail.description).like(pattern),
                func.lower(BookDetail.publisher).like(pattern),
                func.lower(BookDetail.supplier).like(pattern),
            )
        )
    return await apaginate(db, stmt)


@router.get("/{book_id}", response_model=BookWithDetail)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Book detail with nested book_detail (public)."""
    book = await book_service.repository.get_with_detail(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


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
