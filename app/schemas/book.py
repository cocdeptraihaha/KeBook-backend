"""Book schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class BookDetailBase(BaseModel):
    description: Optional[str] = None
    height: Optional[float] = None
    image_url: Optional[str] = None
    length: Optional[float] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None
    supplier: Optional[str] = None
    weight: Optional[float] = None
    width: Optional[float] = None


class BookDetailCreate(BookDetailBase):
    pass


class BookDetail(BookDetailBase):
    id: int

    model_config = {"from_attributes": True}


class BookBase(BaseModel):
    author: Optional[str] = None
    code: Optional[str] = None
    edition: Optional[int] = None
    publication_date: Optional[date] = None
    selling_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    title: Optional[str] = None
    book_detail_id: Optional[int] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    author: Optional[str] = None
    code: Optional[str] = None
    edition: Optional[int] = None
    publication_date: Optional[date] = None
    selling_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    title: Optional[str] = None
    book_detail_id: Optional[int] = None


class Book(BookBase):
    id: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BookWithDetail(Book):
    book_detail: Optional[BookDetail] = None
