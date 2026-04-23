"""Promotion endpoints - mã khuyến mãi."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_superuser, get_current_user_optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.promotion import (
    Promotion,
    PromotionCreate,
    PromotionIssueBody,
    PromotionStatsOut,
    PromotionUpdate,
    PromotionValidate,
)
from app.repositories.promotion_repository import promotion_repository
from app.services.promotion_service import promotion_service

router = APIRouter()


@router.post("/admin/issue", response_model=Promotion, status_code=status.HTTP_201_CREATED)
async def admin_issue_promotion_to_user(
    body: PromotionIssueBody,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    """Tạo mã khuyến mãi cá nhân cho user (sao chép từ promotion mẫu)."""
    try:
        return await promotion_service.issue_personal_copy(
            db, body.user_id, body.promotion_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{promo_id}/stats", response_model=PromotionStatsOut)
async def promotion_usage_stats(
    promo_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    promo = await promotion_repository.get(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
    data = await promotion_service.get_usage_stats(db, promo_id)
    return PromotionStatsOut.model_validate(data)


@router.delete("/{promo_id}", response_model=Promotion)
async def soft_delete_promotion(
    promo_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    promo = await promotion_repository.get(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
    promo.deleted_at = datetime.utcnow()
    await db.flush()
    await db.refresh(promo)
    return promo


@router.get("/validate")
async def validate_promotion(
    code: str = Query(..., description="Promotion code"),
    order_total: float = Query(0, ge=0, description="Order total amount"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Validate promotion code (public - use at checkout). Mã cá nhân cần đăng nhập."""
    uid = current_user.id if current_user else None
    promo, discount, err = await promotion_service.validate_code(
        db, code, order_total, user_id=uid
    )
    if err:
        return {"valid": False, "message": err, "discount_amount": 0}
    return {
        "valid": True,
        "promotion_id": promo.id,
        "discount_amount": round(discount, 2),
        "name": promo.name,
    }


@router.get("/", response_model=list[Promotion])
async def list_promotions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List promotions (admin)."""
    return await promotion_service.get_multi_active(db, skip, limit)


@router.post("/", response_model=Promotion, status_code=201)
async def create_promotion(
    promo_in: PromotionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create promotion (admin)."""
    if promo_in.code:
        promo_in.code = promo_in.code.strip().upper()
    return await promotion_repository.create(db, promo_in)


@router.patch("/{promo_id}", response_model=Promotion)
async def update_promotion(
    promo_id: int,
    promo_in: PromotionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update promotion (admin)."""
    promo = await promotion_repository.get(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return await promotion_repository.update(db, promo, promo_in)
