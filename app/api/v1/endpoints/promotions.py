"""Promotion endpoints - mã khuyến mãi."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.promotion import Promotion, PromotionCreate, PromotionUpdate, PromotionValidate
from app.repositories.promotion_repository import promotion_repository
from app.services.promotion_service import promotion_service

router = APIRouter()


@router.get("/validate")
async def validate_promotion(
    code: str = Query(..., description="Mã khuyến mãi"),
    order_total: float = Query(0, ge=0, description="Tổng tiền đơn hàng"),
    db: AsyncSession = Depends(get_db),
):
    """Kiểm tra mã khuyến mãi (public - dùng khi checkout)."""
    promo, discount, err = await promotion_service.validate_code(
        db, code, order_total
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
    """Danh sách mã khuyến mãi (admin)."""
    return await promotion_service.get_multi_active(db, skip, limit)


@router.post("/", response_model=Promotion, status_code=201)
async def create_promotion(
    promo_in: PromotionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Tạo mã khuyến mãi (admin)."""
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
    """Cập nhật mã khuyến mãi (admin)."""
    promo = await promotion_repository.get(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return await promotion_repository.update(db, promo, promo_in)
