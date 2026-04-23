"""User repository."""
from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreateInDB, UserUpdate
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserCreateInDB, UserUpdate]):
    """Repository cho User."""

    async def get_by_email(
        self, db: AsyncSession, email: str, *, include_deleted: bool = False
    ) -> Optional[User]:
        """Lấy user theo email."""
        stmt = select(User).where(User.email == email)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Lấy user theo username."""
        result = await db.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        return result.scalars().first()

    async def get_by_email_or_username(
        self, db: AsyncSession, email_or_username: str
    ) -> Optional[User]:
        """Lấy user theo email hoặc username (dùng cho login)."""
        result = await db.execute(
            select(User).where(
                or_(
                    User.email == email_or_username,
                    User.username == email_or_username,
                ),
                User.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def list_admin(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 50,
        q: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        include_deleted: bool = False,
    ) -> List[User]:
        stmt = select(User)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if is_superuser is not None:
            stmt = stmt.where(User.is_superuser == is_superuser)
        if q and q.strip():
            term = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    User.email.like(term),
                    User.username.like(term),
                    User.full_name.like(term),
                )
            )
        stmt = stmt.order_by(User.id.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count_admin(
        self,
        db: AsyncSession,
        *,
        q: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        include_deleted: bool = False,
    ) -> int:
        stmt = select(func.count(User.id))
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if is_superuser is not None:
            stmt = stmt.where(User.is_superuser == is_superuser)
        if q and q.strip():
            term = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    User.email.like(term),
                    User.username.like(term),
                    User.full_name.like(term),
                )
            )
        r = await db.execute(stmt)
        return int(r.scalar() or 0)


user_repository = UserRepository(User)
