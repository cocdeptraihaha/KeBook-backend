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
        existing_email = await self.repository.get_by_email(
            db, user_in.email, include_deleted=True
        )
        if existing_email:
            raise ValueError("Email already registered")

        existing_username = await self.repository.get_by_username(db, user_in.username)
        if existing_username:
            raise ValueError("Username already in use")

        data = user_in.model_dump()
        password = data.pop("password")
        data["hashed_password"] = get_password_hash(password)
        user = await self.repository.create(db, UserCreateInDB(**data))
        user.is_active = False
        user.is_superuser = False
        await db.flush()
        await db.refresh(user)
        return user

    async def reset_password(self, db: AsyncSession, user_id: int, new_password: str) -> Optional[User]:
        """Reset password cho user."""
        user = await self.repository.get(db, user_id)
        if not user:
            return None
        user.hashed_password = get_password_hash(new_password)
        await db.flush()
        return user

    async def activate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Kích hoạt tài khoản user."""
        user = await self.repository.get(db, user_id)
        if not user:
            return None
        user.is_active = True
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
        if "email" in data and data["email"] and data["email"] != user.email:
            existing_email = await self.repository.get_by_email(
                db, data["email"], include_deleted=True
            )
            if existing_email and existing_email.id != user_id:
                raise ValueError("Email already registered")
        if "username" in data and data["username"] and data["username"] != user.username:
            existing_username = await self.repository.get_by_username(db, data["username"])
            if existing_username and existing_username.id != user_id:
                raise ValueError("Username already in use")
        if "password" in data:
            data["hashed_password"] = get_password_hash(data.pop("password"))
            data.pop("password", None)
        for key, value in data.items():
            setattr(user, key, value)
        await db.flush()
        await db.refresh(user)
        return user


user_service = UserService()
