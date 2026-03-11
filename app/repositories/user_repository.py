"""User repository."""
from typing import Optional
from sqlalchemy import select, or_
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


user_repository = UserRepository(User)
