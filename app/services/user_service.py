"""User service (business logic)."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserCreateInDB, UserUpdate
from app.repositories.user_repository import user_repository
from app.core.security import get_password_hash


class UserService:
    """Logic nghiệp vụ cho User."""

    def __init__(self):
        self.repository = user_repository

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        """Tạo user mới (hash password)."""
        existing_email = await self.repository.get_by_email(db, user_in.email)
        if existing_email:
            raise ValueError("Email đã được đăng ký")

        existing_username = await self.repository.get_by_username(db, user_in.username)
        if existing_username:
            raise ValueError("Username đã được sử dụng")

        data = user_in.model_dump()
        password = data.pop("password")
        data["hashed_password"] = get_password_hash(password)
        user = await self.repository.create(db, UserCreateInDB(**data))
        user.is_active = False
        user.is_superuser = False
        await db.flush()
        await db.refresh(user)
        return user

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        user_in: UserUpdate,
    ) -> Optional[User]:
        """Cập nhật user."""
        user = await self.repository.get(db, user_id)
        if not user:
            return None

        data = user_in.model_dump(exclude_unset=True)
        if "password" in data:
            data["hashed_password"] = get_password_hash(data.pop("password"))
            data.pop("password", None)
        for key, value in data.items():
            setattr(user, key, value)
        await db.flush()
        await db.refresh(user)
        return user


user_service = UserService()
