"""Notification service."""
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user_notification import UserNotification
from app.schemas.notification import NotificationCreate
from app.repositories.notification_repository import (
    notification_repository,
    user_notification_repository,
)


class NotificationService:
    """Logic nghiệp vụ cho Notification."""

    def __init__(self):
        self.repository = notification_repository
        self.user_notif_repo = user_notification_repository

    async def create_and_send_to_users(
        self,
        db: AsyncSession,
        user_ids: List[int],
        title: str,
        message: str,
        type: str = "INFO",
    ) -> Notification:
        """Tạo thông báo và gửi cho nhiều user."""
        notif = Notification(
            title=title,
            message=message,
            type=type,
            send_date=datetime.utcnow(),
        )
        db.add(notif)
        await db.flush()
        for uid in user_ids:
            un = UserNotification(notification_id=notif.id, user_id=uid)
            db.add(un)
        await db.flush()
        await db.refresh(notif)
        return notif

    async def get_user_notifications(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserNotification]:
        return await self.user_notif_repo.get_by_user(db, user_id, skip, limit)

    async def mark_read(
        self, db: AsyncSession, notification_id: int, user_id: int
    ) -> bool:
        return await self.user_notif_repo.mark_read(
            db, notification_id, user_id
        )


notification_service = NotificationService()
