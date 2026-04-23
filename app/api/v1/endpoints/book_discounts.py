"""Admin: giảm giá theo sách (BookDiscount)."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_superuser
from app.core.database import get_db
from app.models.book_discount import BookDiscount
from app.models.user import User
from app.schemas.book import (
    BookDiscountAdminCreate,
    BookDiscountAdminOut,
    BookDiscountAdminUpdate,
)
from app.services.book_discount_service import book_discount_service

router = APIRouter()


def _to_out(d: BookDiscount) -> BookDiscountAdminOut:
    return BookDiscountAdminOut(
        id=d.id,
        discount_amount=d.discount_amount,
        discount_percent=d.discount_percent,
        start_date=d.start_date,
        end_date=d.end_date,
        book_ids=[b.id for b in (d.books or [])],
    )


@router.get("/", response_model=list[BookDiscountAdminOut])
async def list_book_discounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    rows = await book_discount_service.list_all(
        db, active_only=active_only, skip=skip, limit=limit
    )
    return [_to_out(d) for d in rows]


@router.post("/", response_model=BookDiscountAdminOut, status_code=status.HTTP_201_CREATED)
async def create_book_discount(
    body: BookDiscountAdminCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    try:
        d = await book_discount_service.create(
            db,
            discount_amount=body.discount_amount,
            discount_percent=body.discount_percent,
            start_date=body.start_date,
            end_date=body.end_date,
            book_ids=body.book_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_out(d)


@router.patch("/{discount_id}", response_model=BookDiscountAdminOut)
async def update_book_discount(
    discount_id: int,
    body: BookDiscountAdminUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    patch = body.model_dump(exclude_unset=True)
    try:
        d = await book_discount_service.update(db, discount_id, patch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not d:
        raise HTTPException(status_code=404, detail="BookDiscount not found")
    return _to_out(d)


@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_discount(
    discount_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    ok = await book_discount_service.delete(db, discount_id)
    if not ok:
        raise HTTPException(status_code=404, detail="BookDiscount not found")
    return None
