"""Yêu thích sách."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.book import Book as BookSchema
from app.repositories.book_repository import book_repository
from app.repositories.favorite_repository import favorite_repository

router = APIRouter()


@router.post("/{book_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    book = await book_repository.get(db, book_id)
    if not book or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Book not found")
    await favorite_repository.add(db, current_user.id, book_id)
    return {"ok": True}


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await favorite_repository.remove(db, current_user.id, book_id)
    return None


@router.get("/", response_model=list[BookSchema])
async def list_my_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await favorite_repository.list_by_user(db, current_user.id, skip=skip, limit=limit)


@router.get("/check")
async def check_favorites(
    book_ids: str = Query(..., description="Comma-separated book ids, e.g. 1,2,3"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ids = [int(x.strip()) for x in book_ids.split(",") if x.strip().isdigit()]
    if not ids or len(ids) > 200:
        raise HTTPException(status_code=400, detail="Invalid book_ids")
    m = await favorite_repository.check_map(db, current_user.id, ids)
    return m
