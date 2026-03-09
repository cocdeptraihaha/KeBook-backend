"""Cloudinary upload service."""
import io
import asyncio
from urllib.parse import urlparse

from app.core.config import get_settings

settings = get_settings()

# Lazy init Cloudinary (dùng CLOUDINARY_URL từ settings)
_configured = False


def _ensure_configured() -> None:
    """Đảm bảo Cloudinary đã được config từ settings.CLOUDINARY_URL."""
    global _configured
    if _configured:
        return

    if not settings.CLOUDINARY_URL:
        raise ValueError("CLOUDINARY_URL is not configured")

    import cloudinary

    parsed = urlparse(settings.CLOUDINARY_URL)
    api_key = parsed.username
    api_secret = parsed.password
    cloud_name = parsed.hostname

    if not (api_key and api_secret and cloud_name):
        raise ValueError("CLOUDINARY_URL is invalid (missing api_key / api_secret / cloud_name)")

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )
    _configured = True


def _upload_sync(file_bytes: bytes, folder: str = "kebook-img", resource_type: str = "image") -> dict:
    """Upload ảnh lên Cloudinary (blocking)."""
    import cloudinary.uploader

    _ensure_configured()
    result = cloudinary.uploader.upload(
        io.BytesIO(file_bytes),
        folder=folder,
        resource_type=resource_type,
    )
    return result


def _delete_sync(public_id: str, resource_type: str = "image") -> dict:
    """Xóa ảnh theo public_id (blocking)."""
    import cloudinary.uploader

    _ensure_configured()
    return cloudinary.uploader.destroy(public_id, resource_type=resource_type)


async def upload_image(
    file_bytes: bytes,
    folder: str = "kebook",
) -> str:
    """
    Upload ảnh lên Cloudinary, trả về URL (secure_url).
    Chạy trong thread để không block event loop.
    """
    result = await asyncio.to_thread(_upload_sync, file_bytes, folder=folder)
    return result["secure_url"]


def _public_id_from_url(url: str) -> str | None:
    """
    Rút public_id từ secure_url.
    Ví dụ: https://res.cloudinary.com/<cloud>/image/upload/v123/kebook/avatars/foo.jpg
    -> public_id = kebook/avatars/foo
    """
    try:
        if "/upload/" not in url:
            return None
        after = url.split("/upload/", 1)[1]
        parts = after.split("/")
        # Bỏ v... (version) nếu có
        if parts and parts[0].startswith("v") and parts[0][1:].isdigit():
            parts = parts[1:]
        if not parts:
            return None
        filename = parts[-1]
        name_no_ext = filename.rsplit(".", 1)[0]
        if len(parts) == 1:
            return name_no_ext
        return "/".join(parts[:-1] + [name_no_ext])
    except Exception:
        return None


async def delete_image_by_url(url: str) -> bool:
    """
    Xóa ảnh trên Cloudinary dựa vào secure_url đã lưu trong DB.
    Nếu parse public_id thất bại thì trả False nhưng không ném lỗi.
    """
    public_id = _public_id_from_url(url)
    if not public_id:
        return False
    result = await asyncio.to_thread(_delete_sync, public_id)
    return result.get("result") in {"ok", "not found"}
