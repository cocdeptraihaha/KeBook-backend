"""Address schemas - tỉnh/thành, phường/xã (không dùng quận/huyện)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProvinceItem(BaseModel):
    """Tỉnh/thành phố."""

    code: int
    name: str


class UserAddressBase(BaseModel):
    label: Optional[str] = None
    recipient_name: Optional[str] = None
    phone_number: Optional[str] = None
    address_detail: Optional[str] = None
    ward: Optional[str] = None
    province: Optional[str] = None
    is_default: bool = False


class UserAddressCreate(UserAddressBase):
    pass


class UserAddressUpdate(BaseModel):
    label: Optional[str] = None
    recipient_name: Optional[str] = None
    phone_number: Optional[str] = None
    address_detail: Optional[str] = None
    ward: Optional[str] = None
    province: Optional[str] = None
    is_default: Optional[bool] = None


class UserAddressOut(UserAddressBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WardItem(BaseModel):
    """Phường/xã."""

    code: int
    name: str
