"""Notification service."""
from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User
from app.models.user_notification import UserNotification
from app.schemas.notification import NotificationCreate
from app.repositories.notification_repository import (
    notification_repository,
    user_notification_repository,
)
from app.realtime.connection_manager import connection_manager


class NotificationService:
    """Logic nghiệp vụ cho Notification."""

    def __init__(self):
        self.repository = notification_repository
        self.user_notif_repo = user_notification_repository

    async def _build_new_notif_payload(
        self, db: AsyncSession, notif: Notification, user_id: int
    ) -> dict:
        unread = await self.user_notif_repo.count_unread(db, user_id)
        return {
            "type": "new_notification",
            "id": notif.id,
            "title": notif.title or "",
            "message": notif.message or "",
            "notif_type": notif.type or "INFO",
            "send_date": notif.send_date.isoformat() if notif.send_date else None,
            "unread_count": unread,
        }

    async def push_unread_sync(self, db: AsyncSession, user_id: int) -> None:
        cnt = await self.user_notif_repo.count_unread(db, user_id)
        await connection_manager.send_json_to_user(
            user_id, {"type": "unread_sync", "unread_count": cnt}
        )

    async def create_and_send_to_users(
        self,
        db: AsyncSession,
        user_ids: List[int],
        title: str,
        message: str,
        type: str = "INFO",
    ) -> Notification:
        """Tạo thông báo và gửi cho nhiều user; sau flush đẩy realtime."""
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
        for uid in user_ids:
            payload = await self._build_new_notif_payload(db, notif, uid)
            await connection_manager.send_json_to_user(uid, payload)
        return notif

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Admin: lấy tất cả thông báo."""
        return await self.repository.get_multi_active(db, skip, limit)

    async def get_user_notifications(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserNotification]:
        return await self.user_notif_repo.get_by_user(db, user_id, skip, limit)

    async def mark_read(
        self, db: AsyncSession, notification_id: int, user_id: int
    ) -> bool:
        ok = await self.user_notif_repo.mark_read(db, notification_id, user_id)
        if ok:
            await self.push_unread_sync(db, user_id)
        return ok

    async def mark_all_read(self, db: AsyncSession, user_id: int) -> int:
        n = await self.user_notif_repo.mark_all_read_for_user(db, user_id)
        await self.push_unread_sync(db, user_id)
        return n

    async def get_unread_count(self, db: AsyncSession, user_id: int) -> int:
        return await self.user_notif_repo.count_unread(db, user_id)

    async def get_superuser_ids(self, db: AsyncSession) -> List[int]:
        result = await db.execute(
            select(User.id).where(
                User.is_superuser.is_(True),  # noqa: E712
                User.deleted_at.is_(None),  # noqa: E712
            )
        )
        return [int(r[0]) for r in result.all()]

    async def notify_order_status_for_buyer(
        self,
        db: AsyncSession,
        buyer_user_id: int,
        order_id: int,
        status_label: str,
    ) -> None:
        msg = f"Trạng thái đơn hàng đã cập nhật.\norder_id:{order_id}"
        await self.create_and_send_to_users(
            db,
            [buyer_user_id],
            title=f"Đơn hàng #{order_id}",
            message=msg,
            type="ORDER_STATUS",
        )

    async def notify_checkout_placed_for_buyer(
        self, db: AsyncSession, buyer_user_id: int, order_id: int
    ) -> None:
        msg = f"Đơn của bạn đã được ghi nhận.\norder_id:{order_id}"
        await self.create_and_send_to_users(
            db,
            [buyer_user_id],
            title=f"Đơn hàng #{order_id}",
            message=msg,
            type="ORDER_STATUS",
        )

    async def notify_admins_new_order(self, db: AsyncSession, order_id: int) -> None:
        admin_ids = await self.get_superuser_ids(db)
        if not admin_ids:
            return
        msg = f"Có đơn hàng mới cần xử lý.\norder_id:{order_id}"
        await self.create_and_send_to_users(
            db,
            admin_ids,
            title=f"Đơn mới #{order_id}",
            message=msg,
            type="ORDER_NEW",
        )

    async def notify_admins_new_review(
        self, db: AsyncSession, book_id: int, review_id: int
    ) -> None:
        admin_ids = await self.get_superuser_ids(db)
        if not admin_ids:
            return
        msg = f"Có đánh giá mới.\nbook_id:{book_id}\nreview_id:{review_id}"
        await self.create_and_send_to_users(
            db,
            admin_ids,
            title="Đánh giá mới",
            message=msg,
            type="REVIEW_NEW",
        )

    async def notify_admins_new_support(
        self, db: AsyncSession, support_id: int
    ) -> None:
        admin_ids = await self.get_superuser_ids(db)
        if not admin_ids:
            return
        msg = f"Có yêu cầu hỗ trợ mới.\nsupport_id:{support_id}"
        await self.create_and_send_to_users(
            db,
            admin_ids,
            title="Hỗ trợ",
            message=msg,
            type="SUPPORT_NEW",
        )


notification_service = NotificationService()
