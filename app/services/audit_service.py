"""Ghi nhật ký thao tác admin (bảng admin_audit_log)."""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_audit_log import AdminAuditLog


async def record_admin_audit(
    db: AsyncSession,
    *,
    actor_user_id: Optional[int],
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    payload: Optional[dict[str, Any]] = None,
    ip: Optional[str] = None,
) -> None:
    try:
        row = AdminAuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            payload=payload,
            ip=ip,
            created_at=datetime.utcnow(),
        )
        db.add(row)
        await db.flush()
    except Exception:
        # Không chặn luồng chính nếu bảng chưa migrate
        import logging

        logging.exception("record_admin_audit failed")
