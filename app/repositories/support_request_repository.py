"""SupportRequest repository."""
from typing import List
from sqlalchemy import select
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
    ) -> List[SupportRequest]:
        result = await db.execute(
            select(SupportRequest)
            .order_by(SupportRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


support_request_repository = SupportRequestRepository(SupportRequest)
