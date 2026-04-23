"""SupportRequest schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SupportRequestBase(BaseModel):
    email: Optional[str] = None
    issue: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None


class SupportRequestCreate(SupportRequestBase):
    pass


class SupportRequestUpdate(BaseModel):
    staff_response: Optional[str] = None
    status: Optional[str] = None


class SupportRequestStatusPatch(BaseModel):
    status: str
    note: Optional[str] = None


class SupportRequest(SupportRequestBase):
    id: int
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    staff_id: Optional[int] = None
    staff_name: Optional[str] = None
    staff_response: Optional[str] = None
    status: Optional[str] = None

    model_config = {"from_attributes": True}
