"""Promotion schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PromotionBase(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    discount_percent: Optional[float] = None
    max_discount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    discount_percent: Optional[float] = None
    max_discount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Promotion(PromotionBase):
    id: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PromotionValidate(BaseModel):
    """Request validate mã khuyến mãi."""
    code: str
