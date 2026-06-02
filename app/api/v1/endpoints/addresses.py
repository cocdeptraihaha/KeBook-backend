"""Address endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.address import (
    ProvinceItem,
    UserAddressCreate,
    UserAddressOut,
    UserAddressUpdate,
    WardItem,
)
from app.services.address_service import get_provinces, get_wards_by_province
from app.services.user_address_service import user_address_service

router = APIRouter()


@router.get("/provinces", response_model=list[ProvinceItem])
async def list_provinces():
    """Danh sach tinh/thanh pho Viet Nam (public)."""
    items = await get_provinces()
    return [ProvinceItem(**x) for x in items]


@router.get("/wards", response_model=list[WardItem])
async def list_wards(
    province_id: int = Query(..., description="Ma tinh/thanh"),
):
    """Danh sach phuong/xa theo tinh (public)."""
    items = await get_wards_by_province(province_id)
    return [WardItem(**x) for x in items]


@router.get("/me", response_model=list[UserAddressOut])
async def list_my_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List current user's saved addresses."""
    return await user_address_service.list_for_user(db, current_user.id)


@router.post("/me", response_model=UserAddressOut, status_code=status.HTTP_201_CREATED)
async def create_my_address(
    address_in: UserAddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create saved address for current user."""
    return await user_address_service.create_for_user(db, current_user, address_in)


@router.patch("/me/{address_id}", response_model=UserAddressOut)
async def update_my_address(
    address_id: int,
    address_in: UserAddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's saved address."""
    address = await user_address_service.update_for_user(
        db, current_user.id, address_id, address_in
    )
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.delete("/me/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Soft delete current user's saved address."""
    ok = await user_address_service.soft_delete(db, current_user.id, address_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Address not found")


@router.patch("/me/{address_id}/default", response_model=UserAddressOut)
async def set_my_default_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Set current user's default saved address."""
    address = await user_address_service.set_default(db, current_user.id, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address
