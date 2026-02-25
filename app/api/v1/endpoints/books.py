"""Book endpoints - sách."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.book import Book, BookCreate, BookUpdate, BookWithDetail
from app.services.book_service import book_service

router = APIRouter()


@router.get("/", response_model=list[Book])
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    q: str | None = Query(None, description="Tìm theo title, author"),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách sách (public - không cần auth)."""
    if q:
        books = await book_service.search(db, q=q, skip=skip, limit=limit)
    else:
        books = await book_service.get_multi_active(db, skip=skip, limit=limit)
    return books


@router.get("/{book_id}", response_model=Book)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Chi tiết sách (public)."""
    book = await book_service.repository.get_with_detail(db, book_id)
    if not book or book.is_deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    return book


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Tạo sách mới (chỉ admin)."""
    book = await book_service.create_book(db, book_in)
    return book


@router.patch("/{book_id}", response_model=Book)
async def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Cập nhật sách (chỉ admin)."""
    book = await book_service.repository.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    book = await book_service.repository.update(db, book, book_in)
    return book
