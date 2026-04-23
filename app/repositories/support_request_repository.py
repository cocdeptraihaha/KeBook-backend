"""SupportRequest repository."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.support_request import SupportRequest
from app.schemas.support_request import SupportRequestCreate, SupportRequestUpdate
from app.repositories.base_repository import BaseRepository


class SupportRequestRepository(BaseRepository[SupportRequest, SupportRequestCreate, SupportRequestUpdate]):
    """Repository cho SupportRequest."""

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        q: Optional[str] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ) -> List[SupportRequest]:
        stmt = select(SupportRequest)
        if status and status.strip():
            stmt = stmt.where(SupportRequest.status == status.strip())
        if q and q.strip():
            term = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    SupportRequest.email.like(term),
                    SupportRequest.issue.like(term),
                    SupportRequest.description.like(term),
                )
            )
        if from_dt is not None:
            stmt = stmt.where(SupportRequest.created_at >= from_dt)
        if to_dt is not None:
            stmt = stmt.where(SupportRequest.created_at <= to_dt)
        stmt = stmt.order_by(SupportRequest.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


support_request_repository = SupportRequestRepository(SupportRequest)
