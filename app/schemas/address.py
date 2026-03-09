"""Address schemas - tỉnh/thành, phường/xã (không dùng quận/huyện)."""
from pydantic import BaseModel


class ProvinceItem(BaseModel):
    """Tỉnh/thành phố."""

    code: int
    name: str


class WardItem(BaseModel):
    """Phường/xã."""

    code: int
    name: str
