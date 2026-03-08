"""Category repository."""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    """Repository cho Category."""

    async def get_multi_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Category]:
        """Lấy danh sách category chưa xóa."""
        result = await db.execute(
            select(Category)
            .where(Category.deleted_at.is_(None))  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_roots(self, db: AsyncSession) -> List[Category]:
        """Lấy danh mục gốc (parent_id = None)."""
        result = await db.execute(
            select(Category).where(
                Category.parent_id.is_(None),
                Category.deleted_at.is_(None),  # noqa: E712
            )
        )
        return list(result.scalars().all())


category_repository = CategoryRepository(Category)
