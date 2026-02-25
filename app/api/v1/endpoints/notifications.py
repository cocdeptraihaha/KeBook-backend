"""Notification endpoints - thông báo."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import Notification, NotificationCreate, NotificationSendRequest
from app.services.notification_service import notification_service
from app.repositories.notification_repository import notification_repository

router = APIRouter()


@router.get("/me")
async def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lấy thông báo của user đăng nhập."""
    return await notification_service.get_user_notifications(
        db, current_user.id, skip, limit
    )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Đánh dấu đã đọc."""
    ok = await notification_service.mark_read(
        db, notification_id, current_user.id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")
    return {"message": "Đã đánh dấu đọc"}


@router.get("/", response_model=list[Notification])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Danh sách thông báo (admin)."""
    return await notification_repository.get_multi_active(db, skip, limit)


@router.post("/", response_model=Notification, status_code=201)
async def create_notification(
    body: NotificationSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Tạo thông báo và gửi cho user_ids (admin)."""
    if not body.user_ids:
        raise HTTPException(status_code=400, detail="Cần có ít nhất 1 user_id")
    return await notification_service.create_and_send_to_users(
        db,
        body.user_ids,
        title=body.title or "",
        message=body.message or "",
        type=body.type or "INFO",
    )
