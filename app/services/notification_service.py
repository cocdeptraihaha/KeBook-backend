"""Notification service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.business_rules import NOTIFICATION_WS_SCHEMA_VERSION
from app.models.notification import Notification
from app.models.user import User
from app.models.user_notification import UserNotification
from app.repositories.notification_repository import (
    notification_repository,
    user_notification_repository,
)
from app.realtime.connection_manager import connection_manager
from app.schemas.notification import NotificationType

ORDER_STATUS_TO_NOTIF_TYPE: dict[str, NotificationType] = {
    "PENDING": NotificationType.ORDER_STATUS_PENDING,
    "CONFIRMED": NotificationType.ORDER_STATUS_CONFIRMED,
    "INPROGRESS": NotificationType.ORDER_STATUS_INPROGRESS,
    "SHIPPED": NotificationType.ORDER_STATUS_SHIPPED,
    "DELIVERED": NotificationType.ORDER_STATUS_DELIVERED,
    "COMPLETED": NotificationType.ORDER_STATUS_COMPLETED,
    "CANCELLED": NotificationType.ORDER_STATUS_CANCELLED,
    "CANCEL_REQUESTED": NotificationType.ORDER_STATUS_CANCEL_REQUESTED,
    "RETURNED": NotificationType.ORDER_STATUS_RETURNED,
}


def _safe_notification_type(value: Optional[str]) -> str:
    raw = str(value or "").strip()
    if raw in NotificationType._value2member_map_:
        return raw
    return NotificationType.GENERIC.value


class NotificationService:
    """Business logic for Notification."""

    def __init__(self):
        self.repository = notification_repository
        self.user_notif_repo = user_notification_repository

    @staticmethod
    def _payload_from_message(message: Optional[str]) -> Dict[str, Any]:
        """Parse JSON payload from message; fallback key:value lines."""
        out: Dict[str, Any] = {}
        if not message:
            return out

        m = message.strip()
        if not m:
            return out

        if (m.startswith("{") and m.endswith("}")) or (m.startswith("[") and m.endswith("]")):
            try:
                parsed = json.loads(m)
                if isinstance(parsed, dict):
                    return parsed
                return {"value": parsed}
            except Exception:
                pass

        for line in m.split("\n"):
            part = line.strip()
            if ":" not in part:
                continue
            key, _, rest = part.partition(":")
            k = key.strip()
            v = rest.strip()
            if not k:
                continue
            if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                out[k] = int(v)
            else:
                out[k] = v
        return out

    @staticmethod
    def _message_from_payload(payload: Optional[Dict[str, Any]]) -> str:
        if not payload:
            return "{}"
        return json.dumps(payload, ensure_ascii=False)

    async def _build_new_notif_payload(
        self, db: AsyncSession, notif: Notification, user_id: int
    ) -> dict:
        unread = await self.user_notif_repo.count_unread(db, user_id)
        payload = self._payload_from_message(notif.message or "")
        return {
            "type": "new_notification",
            "schema_version": NOTIFICATION_WS_SCHEMA_VERSION,
            "id": notif.id,
            "title": notif.title or "",
            "message": notif.message or "",
            "notif_type": notif.type or NotificationType.GENERIC.value,
            "send_date": notif.send_date.isoformat() if notif.send_date else None,
            "unread_count": unread,
            "payload": payload,
            "meta": payload,
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
        message: str = "",
        type: str = NotificationType.GENERIC.value,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Create notification and send realtime to many users."""
        final_message = self._message_from_payload(payload) if payload is not None else (message or "{}")
        notif = Notification(
            title=title,
            message=final_message,
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
            ws_payload = await self._build_new_notif_payload(db, notif, uid)
            await connection_manager.send_json_to_user(uid, ws_payload)
        return notif

    async def resolve_broadcast_recipient_ids(
        self,
        db: AsyncSession,
        user_ids: Optional[List[int]],
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> List[int]:
        if user_ids:
            return sorted({int(x) for x in user_ids})
        stmt = select(User.id).where(User.deleted_at.is_(None))
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if is_superuser is not None:
            stmt = stmt.where(User.is_superuser == is_superuser)
        r = await db.execute(stmt)
        return [int(x[0]) for x in r.all()]

    async def broadcast(
        self,
        db: AsyncSession,
        *,
        title: str,
        message: str,
        type: str = NotificationType.GENERIC.value,
        user_ids: Optional[List[int]] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> Notification:
        ids = await self.resolve_broadcast_recipient_ids(
            db, user_ids, is_active=is_active, is_superuser=is_superuser
        )
        if not ids:
            raise ValueError("Khong co nguoi nhan")
        return await self.create_and_send_to_users(db, ids, title, message, type, payload=None)

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        return await self.repository.get_multi_active(db, skip, limit)

    async def get_user_notifications(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserNotification]:
        return await self.user_notif_repo.get_by_user(db, user_id, skip, limit)

    def map_user_notifications_for_api(self, rows: List[UserNotification]) -> List[dict]:
        out: List[dict] = []
        for un in rows:
            notif = un.notification
            payload = self._payload_from_message((notif.message if notif else "") or "")
            notif_type = _safe_notification_type(notif.type if notif else None)
            out.append(
                {
                    "notification_id": un.notification_id,
                    "user_id": un.user_id,
                    "is_read": un.is_read,
                    "read_at": un.read_at,
                    "notification": {
                        "id": notif.id if notif else un.notification_id,
                        "title": (notif.title if notif else "") or "",
                        "message": (notif.message if notif else "") or "",
                        "type": notif_type,
                        "send_date": notif.send_date if notif else None,
                        "deleted_at": notif.deleted_at if notif else None,
                        "payload": payload,
                    },
                }
            )
        return out

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
                User.is_superuser.is_(True),
                User.deleted_at.is_(None),
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
        raw = (status_label or "").upper()
        notif_type = ORDER_STATUS_TO_NOTIF_TYPE.get(raw, NotificationType.GENERIC)
        await self.create_and_send_to_users(
            db,
            [buyer_user_id],
            title=f"ORDER #{order_id}",
            type=notif_type.value,
            payload={"order_id": order_id, "status": raw},
        )

    async def notify_checkout_placed_for_buyer(
        self, db: AsyncSession, buyer_user_id: int, order_id: int
    ) -> None:
        await self.create_and_send_to_users(
            db,
            [buyer_user_id],
            title=f"ORDER #{order_id}",
            type=NotificationType.ORDER_NEW.value,
            payload={"order_id": order_id},
        )

    async def notify_admins_new_order(self, db: AsyncSession, order_id: int) -> None:
        admin_ids = await self.get_superuser_ids(db)
        if not admin_ids:
            return
        await self.create_and_send_to_users(
            db,
            admin_ids,
            title=f"ORDER #{order_id}",
            type=NotificationType.ORDER_NEW.value,
            payload={"order_id": order_id},
        )

    async def notify_admins_new_review(
        self, db: AsyncSession, book_id: int, review_id: int
    ) -> None:
        admin_ids = await self.get_superuser_ids(db)
        if not admin_ids:
            return
        await self.create_and_send_to_users(
            db,
            admin_ids,
            title="REVIEW_NEW",
            type=NotificationType.REVIEW_NEW.value,
            payload={"book_id": book_id, "review_id": review_id},
        )

    async def notify_admins_new_support(
        self, db: AsyncSession, support_id: int
    ) -> None:
        admin_ids = await self.get_superuser_ids(db)
        if not admin_ids:
            return
        await self.create_and_send_to_users(
            db,
            admin_ids,
            title="SUPPORT_NEW",
            type=NotificationType.SUPPORT_NEW.value,
            payload={"support_id": support_id},
        )


notification_service = NotificationService()
