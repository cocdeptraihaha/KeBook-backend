"""Base repository cho CRUD."""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import Base as ModelBase

ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository CRUD."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Lấy theo ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Lấy danh sách."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Tạo mới."""
        data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
        db_obj = self.model(**data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Cập nhật."""
        data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Xóa theo ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            return True
        return False
