"""Notification repository."""
from datetime import datetime
from typing import List

from sqlalchemy import func, or_, select
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

    async def count_unread(self, db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(UserNotification)
            .join(Notification, UserNotification.notification_id == Notification.id)
            .where(
                UserNotification.user_id == user_id,
                Notification.deleted_at.is_(None),  # noqa: E712
                or_(
                    UserNotification.is_read.is_(None),
                    UserNotification.is_read.is_(False),
                ),
            )
        )
        return int(result.scalar() or 0)

    async def mark_all_read_for_user(self, db: AsyncSession, user_id: int) -> int:
        """Đánh dấu đã đọc mọi thông báo còn unread của user. Trả số bản ghi cập nhật."""
        result = await db.execute(
            select(UserNotification)
            .join(Notification, UserNotification.notification_id == Notification.id)
            .where(
                UserNotification.user_id == user_id,
                Notification.deleted_at.is_(None),  # noqa: E712
                or_(
                    UserNotification.is_read.is_(None),
                    UserNotification.is_read.is_(False),
                ),
            )
        )
        rows = list(result.scalars().all())
        now = datetime.utcnow()
        for un in rows:
            un.is_read = True
            un.read_at = now
        await db.flush()
        return len(rows)


notification_repository = NotificationRepository(Notification)
user_notification_repository = UserNotificationRepository()
