"""Test-only endpoints - for automation testing."""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.otp import OTP
from app.models.user import User
from app.schemas.book import Book as BookSchema, BookCreate
from app.services.book_service import book_service

router = APIRouter()


def _is_test_env() -> bool:
    return os.getenv("TESTING") == "1" or "test.db" in os.getenv("DATABASE_URL", "")


@router.get("/otp")
async def get_otp_for_test(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """Lấy OTP mới nhất cho email (chỉ khi TESTING=1 hoặc dùng test.db)."""
    if not _is_test_env():
        return {"error": "Not available"}
    result = await db.execute(
        select(OTP).where(OTP.email == email).order_by(OTP.created_at.desc())
    )
    otp = result.scalars().first()
    return {"otp_code": otp.code if otp else None}


@router.post("/make-admin")
async def make_admin_for_test(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """Set is_superuser=True for user (only when TESTING=1)."""
    if not _is_test_env():
        return {"error": "Not available"}
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        return {"error": "User not found"}
    user.is_superuser = True
    await db.commit()
    return {"ok": True}


@router.post("/books", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book_for_test(
    book_in: BookCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create book without token (only when TESTING=1 or test.db)."""
    if not _is_test_env():
        raise HTTPException(status_code=403, detail="Not available - use TESTING=1 or test.db")
    book = await book_service.create_book(db, book_in)
    await db.commit()
    return book
