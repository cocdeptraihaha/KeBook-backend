"""Address endpoints - tỉnh/thành, phường/xã (không dùng quận/huyện, khớp với DB users)."""
from fastapi import APIRouter, Query

from app.schemas.address import ProvinceItem, WardItem
from app.services.address_service import get_provinces, get_wards_by_province

router = APIRouter()


@router.get("/provinces", response_model=list[ProvinceItem])
async def list_provinces():
    """Danh sách tỉnh/thành Việt Nam (public)."""
    items = await get_provinces()
    return [ProvinceItem(**x) for x in items]


@router.get("/wards", response_model=list[WardItem])
async def list_wards(
    province_id: int = Query(..., description="Mã tỉnh/thành"),
):
    """Danh sách phường/xã theo tỉnh (public). Khớp với DB: province + ward."""
    items = await get_wards_by_province(province_id)
    return [WardItem(**x) for x in items]
