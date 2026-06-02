"""Promotion schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PromotionBase(BaseModel):
    owner_user_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    free_shipping: bool = False
    max_discount: Optional[float] = None
    min_order_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    free_shipping: Optional[bool] = None
    max_discount: Optional[float] = None
    min_order_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class Promotion(PromotionBase):
    id: int
    used_count: int = 0
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PromotionValidate(BaseModel):
    """Request validate mã khuyến mãi."""
    code: str


class PromotionStatsOut(BaseModel):
    promotion_id: int
    usage_count: int
    total_discount: float


class PromotionIssueBody(BaseModel):
    user_id: int
    promotion_id: int
