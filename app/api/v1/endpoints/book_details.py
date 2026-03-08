"""Book detail endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.book import BookDetail, BookDetailCreate, BookDetailUpdate
from app.repositories.book_repository import book_detail_repository

router = APIRouter()


@router.get("/", response_model=list[BookDetail])
async def list_book_details(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List all book details (admin)."""
    return await book_detail_repository.get_multi(db, skip, limit)


@router.get("/{detail_id}", response_model=BookDetail)
async def get_book_detail(
    detail_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Get book detail by ID (admin)."""
    detail = await book_detail_repository.get(db, detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Book detail not found")
    return detail


@router.post("/", response_model=BookDetail, status_code=status.HTTP_201_CREATED)
async def create_book_detail(
    detail_in: BookDetailCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create book detail (admin). Returns detail with id for linking to book."""
    return await book_detail_repository.create(db, detail_in)


@router.patch("/{detail_id}", response_model=BookDetail)
async def update_book_detail(
    detail_id: int,
    detail_in: BookDetailUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update book detail (admin)."""
    detail = await book_detail_repository.get(db, detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Book detail not found")
    return await book_detail_repository.update(db, detail, detail_in)
