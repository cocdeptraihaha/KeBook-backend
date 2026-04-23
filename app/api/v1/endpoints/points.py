"""Đổi điểm tích lũy lấy voucher."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.point_reward import PointReward
from app.models.user import User
from app.schemas.point_reward import (
    PointRewardCreate,
    PointRewardOut,
    PointRewardUpdate,
    RedeemRewardOut,
)
from app.repositories.point_reward_repository import point_reward_repository
from app.services.reward_service import reward_service

router = APIRouter()


@router.get("/admin/rewards", response_model=list[PointRewardOut])
async def admin_list_point_rewards(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return await point_reward_repository.list_all(db, skip=skip, limit=limit)


@router.post("/admin/rewards", response_model=PointRewardOut, status_code=status.HTTP_201_CREATED)
async def admin_create_point_reward(
    body: PointRewardCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    row = PointReward(
        name=body.name,
        cost_points=body.cost_points,
        discount_percent=float(body.discount_percent),
        max_discount=body.max_discount,
        valid_days=max(1, int(body.valid_days or 30)),
        active=bool(body.active),
    )
    return await point_reward_repository.create(db, row)


@router.patch("/admin/rewards/{reward_id}", response_model=PointRewardOut)
async def admin_update_point_reward(
    reward_id: int,
    body: PointRewardUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    patch = body.model_dump(exclude_unset=True)
    row = await point_reward_repository.update_fields(db, reward_id, patch)
    if not row:
        raise HTTPException(status_code=404, detail="Point reward not found")
    return row


@router.get("/rewards", response_model=list[PointRewardOut])
async def list_point_rewards(db: AsyncSession = Depends(get_db)):
    """Danh sách gói đổi điểm (public)."""
    return await point_reward_repository.list_active(db)


@router.post("/rewards/{reward_id}/redeem", response_model=RedeemRewardOut)
async def redeem_point_reward(
    reward_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        promo, bal = await reward_service.redeem(db, current_user.id, reward_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedeemRewardOut(
        promotion_id=promo.id,
        code=promo.code or "",
        name=promo.name,
        discount_percent=promo.discount_percent,
        max_discount=promo.max_discount,
        end_date=promo.end_date,
        points_balance_after=bal,
    )
