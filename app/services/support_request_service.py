"""SupportRequest service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.support_request import SupportRequest
from app.schemas.support_request import SupportRequestCreate, SupportRequestUpdate
from app.repositories.support_request_repository import support_request_repository


class SupportRequestService:
    """Logic nghiệp vụ cho SupportRequest."""

    def __init__(self):
        self.repository = support_request_repository

    async def create(
        self,
        db: AsyncSession,
        req_in: SupportRequestCreate,
        user_email: str,
    ) -> SupportRequest:
        """User tạo yêu cầu hỗ trợ."""
        req = SupportRequest(
            email=req_in.email or user_email,
            issue=req_in.issue,
            description=req_in.description,
            type=req_in.type,
            created_at=datetime.utcnow(),
            status="PENDING",
        )
        db.add(req)
        await db.flush()
        await db.refresh(req)
        try:
            from app.services.notification_service import notification_service

            await notification_service.notify_admins_new_support(db, req.id)
        except Exception:
            import logging

            logging.exception("notify_admins_new_support failed")
        return req

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[SupportRequest]:
        return await self.repository.get_multi(db, skip, limit)

    async def respond(
        self,
        db: AsyncSession,
        req_id: int,
        req_in: SupportRequestUpdate,
        staff_id: int,
        staff_name: str,
    ) -> Optional[SupportRequest]:
        """Admin phản hồi yêu cầu hỗ trợ."""
        req = await self.repository.get(db, req_id)
        if not req:
            return None
        if req_in.staff_response is not None:
            req.staff_response = req_in.staff_response
            req.staff_id = staff_id
            req.staff_name = staff_name
        if req_in.status is not None:
            req.status = req_in.status
            if req_in.status == "RESOLVED":
                req.resolved_at = datetime.utcnow()
        await db.flush()
        await db.refresh(req)
        return req


support_request_service = SupportRequestService()
