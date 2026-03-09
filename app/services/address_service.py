"""Address service - tỉnh/thành, phường/xã từ provinces.open-api.vn API v2 (sau sáp nhập 07/2025)."""
from typing import Any

import httpx

# API v2: sau sáp nhập tỉnh thành 07/2025, cấu trúc province -> wards trực tiếp (không districts)
BASE_URL = "https://provinces.open-api.vn/api/v2"

# Cache in-memory (load 1 lần khi có request đầu tiên, depth=2: province -> wards)
_address_cache: list[dict[str, Any]] | None = None


async def _fetch_json(url: str) -> list[dict] | dict:
    """Fetch JSON từ API."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def _ensure_cache_loaded() -> list[dict[str, Any]]:
    """Load provinces + wards (depth=2) 1 lần, cache lại. V2: province có wards trực tiếp."""
    global _address_cache
    if _address_cache is None:
        data = await _fetch_json(f"{BASE_URL}/?depth=2")
        _address_cache = data if isinstance(data, list) else []
    return _address_cache


async def get_provinces() -> list[dict[str, Any]]:
    """Danh sách tỉnh/thành (sau sáp nhập). Trả về [{code, name}, ...]."""
    data = await _ensure_cache_loaded()
    return [{"code": p["code"], "name": p["name"]} for p in data]


async def get_wards_by_province(province_id: int) -> list[dict[str, Any]]:
    """Danh sách phường/xã theo tỉnh. V2: wards nằm trực tiếp trong province."""
    data = await _ensure_cache_loaded()
    for p in data:
        if p["code"] == province_id:
            wards = p.get("wards") or []
            return [{"code": w["code"], "name": w["name"]} for w in wards]
    return []
