"""ReturnRequest schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReturnRequestBase(BaseModel):
    quantity: int = 1
    reason: Optional[str] = None


class ReturnRequestCreate(ReturnRequestBase):
    order_id: int
    order_item_id: int


class ReturnRequestUpdate(BaseModel):
    status: Optional[str] = None  # APPROVED, PENDING, REJECTED


class ReturnRequestProcess(BaseModel):
    status: str  # APPROVED, REJECTED


class ReturnRequest(ReturnRequestBase):
    id: int
    order_id: int
    order_item_id: int
    request_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    status: str
    processed_by: Optional[int] = None

    model_config = {"from_attributes": True}


class ReturnRequestAdminRow(ReturnRequest):
    """Return request kèm thông tin khách và tên sách cho admin."""

    buyer_email: Optional[str] = None
    buyer_full_name: Optional[str] = None
    book_title: Optional[str] = None
