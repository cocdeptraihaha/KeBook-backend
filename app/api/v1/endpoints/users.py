"""User endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Đăng ký user mới."""
    try:
        user = await user_service.create_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserSchema)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Lấy thông tin user đang đăng nhập."""
    return current_user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy user theo ID."""
    user = await user_service.repository.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
    return user


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật user (chỉ cho chính mình)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền")
    user = await user_service.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xóa user (chỉ cho chính mình)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền")
    deleted = await user_service.repository.delete(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
