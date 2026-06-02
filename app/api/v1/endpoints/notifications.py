"""Notification endpoints - thông báo."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import (
    Notification,
    NotificationBroadcastRequest,
    NotificationSendRequest,
    UserNotificationOut,
)
from app.services.notification_service import notification_service

router = APIRouter()


@router.get("/me/unread-count")
async def get_my_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Số thông báo chưa đọc."""
    count = await notification_service.get_unread_count(db, current_user.id)
    return {"count": count}


@router.post("/me/read-all")
async def mark_all_my_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Đánh dấu tất cả thông báo của user là đã đọc."""
    n = await notification_service.mark_all_read(db, current_user.id)
    return {"updated": n}


@router.get("/me", response_model=list[UserNotificationOut])
async def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get notifications of logged-in user."""
    rows = await notification_service.get_user_notifications(
        db, current_user.id, skip, limit
    )
    return notification_service.map_user_notifications_for_api(rows)


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark as read."""
    ok = await notification_service.mark_read(
        db, notification_id, current_user.id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Marked as read"}


@router.get("/", response_model=list[Notification])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List notifications (admin)."""
    return await notification_service.get_all(db, skip, limit)


@router.post("/", response_model=Notification, status_code=201)
async def create_notification(
    body: NotificationSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create notification and send to user_ids (admin)."""
    if not body.user_ids:
        raise HTTPException(status_code=400, detail="At least 1 user_id is required")
    return await notification_service.create_and_send_to_users(
        db,
        body.user_ids,
        title=body.title or "",
        message=body.message or "",
        type=body.type or "GENERIC",
    )


@router.post("/broadcast", response_model=Notification, status_code=201)
async def broadcast_notification(
    body: NotificationBroadcastRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    """Gửi thông báo tới user_ids, hoặc lọc user_filter, hoặc toàn bộ user (không truyền cả hai)."""
    uf = body.user_filter
    is_active = uf.is_active if uf else None
    is_superuser = uf.is_superuser if uf else None
    try:
        return await notification_service.broadcast(
            db,
            title=body.title or "",
            message=body.message or "",
            type=body.type or "GENERIC",
            user_ids=body.user_ids,
            is_active=is_active,
            is_superuser=is_superuser,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
