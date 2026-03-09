"""Upload ảnh lên Cloudinary, trả về URL (và có thể lưu vào DB)."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.dependencies import get_current_active_user, get_current_superuser
from app.models.user import User
from app.models.book_detail import BookDetail as BookDetailModel
from app.services.cloudinary_service import upload_image, delete_image_by_url
from app.services.user_service import user_service
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_SIZE_MB = 5


class UploadResponse(BaseModel):
    """Response sau khi upload ảnh."""
    url: str


class UploadAvatarResponse(BaseModel):
    """Response upload avatar: URL + đã cập nhật user."""
    url: str
    avatar_url: str  # giá trị đã lưu vào DB


@router.post("/image", response_model=UploadResponse)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    folder: str = "kebook",
    current_user: User = Depends(get_current_active_user),
):
    """
    Nhận ảnh từ frontend (multipart), upload lên Cloudinary, trả về URL.
    Frontend dùng URL này để PATCH user (avatar_url) hoặc book_detail (image_url), v.v.
    """
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )
    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_SIZE_MB}MB)")
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        url = await upload_image(file_bytes=content, folder=folder)
        return UploadResponse(url=url)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/avatar", response_model=UploadAvatarResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload ảnh lên Cloudinary và lưu URL vào user.avatar_url (DB).
    """
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )
    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_SIZE_MB}MB)")
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        url = await upload_image(file_bytes=content, folder="kebook/avatars")
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Lưu URL vào DB (và xóa ảnh cũ nếu có)
    user = await user_service.repository.get(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.avatar_url:
        # Xóa ảnh cũ trên Cloudinary (nếu parse public_id được)
        await delete_image_by_url(user.avatar_url)
    user.avatar_url = url
    await db.flush()
    await db.refresh(user)

    return UploadAvatarResponse(url=url, avatar_url=url)


class UploadBookDetailImageResponse(BaseModel):
    """Response upload ảnh book detail: URL + đã cập nhật book_detail."""
    url: str
    image_url: str
    detail_id: int


@router.post("/book-detail/{detail_id}/image", response_model=UploadBookDetailImageResponse)
async def upload_book_detail_image(
    detail_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Upload ảnh lên Cloudinary và lưu URL vào book_details.image_url (DB).
    Admin-only vì book_detail là dữ liệu catalog.
    """
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )
    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_SIZE_MB}MB)")
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        url = await upload_image(file_bytes=content, folder="kebook/book-details")
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))

    detail = await db.get(BookDetailModel, detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Book detail not found")
    if detail.image_url:
        await delete_image_by_url(detail.image_url)
    detail.image_url = url
    await db.flush()
    await db.refresh(detail)
    return UploadBookDetailImageResponse(url=url, image_url=url, detail_id=detail_id)
