"""Cart schemas."""
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from app.schemas.book import Book


class CartBase(BaseModel):
    quantity: Optional[int] = None
    book_id: int = 0
    user_id: int = 0


class CartCreate(BaseModel):
    book_id: int
    quantity: int = 1
    user_id: int = 0  # set by service


class CartUpdate(BaseModel):
    quantity: Optional[int] = None


class Cart(CartBase):
    id: int
    create_at: Optional[date] = None
    update_at: Optional[date] = None
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CartWithBook(Cart):
    book: Optional["Book"] = None
