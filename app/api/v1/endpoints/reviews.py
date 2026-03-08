"""Review endpoints - đánh giá sách."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import review_service

router = APIRouter()


@router.get("/book/{book_id}", response_model=list[Review])
async def list_reviews_by_book(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List reviews by book (public)."""
    return await review_service.get_by_book(db, book_id, skip, limit)


@router.get("/book/{book_id}/avg")
async def get_book_avg_rate(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Average rating of book (public)."""
    avg = await review_service.get_avg_rate(db, book_id)
    return {"book_id": book_id, "avg_rate": round(float(avg), 2) if avg else None}


@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create review (user must have purchased to review)."""
    try:
        return await review_service.create_review(db, review_in, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{review_id}", response_model=Review)
async def update_review(
    review_id: int,
    review_in: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update review (own reviews only)."""
    review = await review_service.update_review(
        db, review_id, current_user.id, review_in
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete review (own reviews only)."""
    ok = await review_service.delete_review(db, review_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Review not found")
