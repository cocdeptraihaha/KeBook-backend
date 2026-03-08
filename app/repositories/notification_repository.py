"""Notification repository."""
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user_notification import UserNotification
from app.schemas.notification import NotificationCreate
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification, NotificationCreate, NotificationCreate]):
    """Repository cho Notification."""

    async def get_multi_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Notification]:
        result = await db.execute(
            select(Notification)
            .where(Notification.deleted_at.is_(None))  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


class UserNotificationRepository:
    """Repository cho UserNotification (composite PK)."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserNotification]:
        result = await db.execute(
            select(UserNotification)
            .where(UserNotification.user_id == user_id)
            .options(selectinload(UserNotification.notification))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_read(
        self, db: AsyncSession, notification_id: int, user_id: int
    ) -> bool:
        from datetime import datetime
        result = await db.execute(
            select(UserNotification).where(
                UserNotification.notification_id == notification_id,
                UserNotification.user_id == user_id,
            )
        )
        un = result.scalars().first()
        if not un:
            return False
        un.is_read = True
        un.read_at = datetime.utcnow()
        await db.flush()
        return True


notification_repository = NotificationRepository(Notification)
user_notification_repository = UserNotificationRepository()
