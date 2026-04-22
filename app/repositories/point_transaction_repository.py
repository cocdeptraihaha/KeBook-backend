"""Point transaction repository."""
from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.point_transaction import PointTransaction


class PointTransactionRepository:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        delta: int,
        reason: str,
        ref_type: str | None,
        ref_id: int | None,
        balance_after: int,
    ) -> PointTransaction:
        row = PointTransaction(
            user_id=user_id,
            delta=delta,
            reason=reason,
            ref_type=ref_type,
            ref_id=ref_id,
            balance_after=balance_after,
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    async def list_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[PointTransaction]:
        r = await db.execute(
            select(PointTransaction)
            .where(PointTransaction.user_id == user_id)
            .order_by(desc(PointTransaction.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(r.scalars().all())


point_transaction_repository = PointTransactionRepository()
