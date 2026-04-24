"""Point transaction repository."""
from typing import List, Optional
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

    async def exists_for_ref(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        reason: str,
        ref_type: Optional[str],
        ref_id: Optional[int],
    ) -> bool:
        """Idempotency: đã có giao dịch cùng reason + ref?"""
        stmt = select(PointTransaction.id).where(
            PointTransaction.user_id == user_id,
            PointTransaction.reason == reason,
        )
        if ref_type is not None:
            stmt = stmt.where(PointTransaction.ref_type == ref_type)
        else:
            stmt = stmt.where(PointTransaction.ref_type.is_(None))
        if ref_id is not None:
            stmt = stmt.where(PointTransaction.ref_id == ref_id)
        else:
            stmt = stmt.where(PointTransaction.ref_id.is_(None))
        r = await db.execute(stmt.limit(1))
        return r.scalar_one_or_none() is not None

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
