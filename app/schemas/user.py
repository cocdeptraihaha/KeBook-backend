"""User schemas - khớp với database."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema khi tạo user."""

    password: str


class UserCreateInDB(BaseModel):
    """Schema nội bộ khi tạo user (đã hash password)."""

    email: str
    username: str
    full_name: Optional[str] = None
    hashed_password: str


class UserUpdate(BaseModel):
    """Schema khi cập nhật user."""

    password: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None


class User(UserBase):
    """Schema response user (không có password)."""

    id: int
    is_active: bool = False
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserInDB(User):
    """User với hashed_password (nội bộ)."""

    hashed_password: str
