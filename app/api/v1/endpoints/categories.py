"""Category endpoints - danh mục sách."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_superuser
from app.core.database import get_db
from app.models.user import User
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.repositories.category_repository import category_repository

router = APIRouter()


@router.get("/", response_model=list[Category])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách danh mục (public)."""
    return await category_repository.get_multi_active(db, skip, limit)


@router.get("/roots", response_model=list[Category])
async def list_root_categories(db: AsyncSession = Depends(get_db)):
    """Danh mục gốc (public)."""
    return await category_repository.get_roots(db)


@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Chi tiết danh mục (public)."""
    cat = await category_repository.get(db, category_id)
    if not cat or cat.is_deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    return cat


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Tạo danh mục (chỉ admin)."""
    return await category_repository.create(db, category_in)


@router.patch("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Cập nhật danh mục (chỉ admin)."""
    cat = await category_repository.get(db, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    return await category_repository.update(db, cat, category_in)
