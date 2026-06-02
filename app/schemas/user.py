"""User schemas - khớp với database."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date


class UserBase(BaseModel):
    """Base user schema."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    ward: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime | date] = None  # MySQL DATE -> date, DATETIME -> datetime
    gender: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(BaseModel):
    """Schema khi tạo user."""

    email: EmailStr
    username: str
    full_name: Optional[str] = None
    password: str


class UserCreateInDB(BaseModel):
    """Schema nội bộ khi tạo user (đã hash password)."""

    email: str
    username: str
    full_name: Optional[str] = None
    hashed_password: str


class UserUpdate(BaseModel):
    """Schema khi cập nhật user."""

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    ward: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime | date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None


class User(UserBase):
    """Schema response user (không có password)."""

    id: int
    is_active: bool = False
    is_superuser: bool = False
    loyalty_points: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserInDB(User):
    """User với hashed_password (nội bộ)."""

    hashed_password: str


class AdminUserStatusBody(BaseModel):
    is_active: bool


class AdminUserRoleBody(BaseModel):
    is_superuser: bool


class AdminPointsAdjustBody(BaseModel):
    delta: int
    reason: str
