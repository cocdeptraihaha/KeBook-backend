"""Review schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    content: Optional[str] = None
    rate: Optional[int] = Field(None, ge=1, le=5)


class ReviewCreate(ReviewBase):
    book_id: int
    user_id: Optional[int] = None  # set by service


class ReviewUpdate(BaseModel):
    content: Optional[str] = None
    rate: Optional[int] = Field(None, ge=1, le=5)


class Review(ReviewBase):
    id: int
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    create_at: Optional[datetime] = None
    is_deleted: bool = False

    model_config = {"from_attributes": True}


class ReviewWithUser(Review):
    user: Optional["UserBrief"] = None


class UserBrief(BaseModel):
    id: int
    full_name: Optional[str] = None
    username: Optional[str] = None

    model_config = {"from_attributes": True}
