"""Đổi điểm tích lũy lấy voucher."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.point_reward import PointRewardOut, RedeemRewardOut
from app.repositories.point_reward_repository import point_reward_repository
from app.services.reward_service import reward_service

router = APIRouter()


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
