"""User endpoints."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.user_service import user_service

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Get logged-in user info."""
    return current_user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by ID (self or admin only)."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Permission denied")
    user = await user_service.repository.get(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user (own profile only)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    user = await user_service.update_user(db, user_id, user_in)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete user (own account only)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    user = await user_service.repository.get(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")

    user.deleted_at = datetime.utcnow()
    await db.flush()
