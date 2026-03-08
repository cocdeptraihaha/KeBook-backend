"""Category schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class Category(CategoryBase):
    id: int
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CategoryWithChildren(Category):
    children: List["Category"] = []
