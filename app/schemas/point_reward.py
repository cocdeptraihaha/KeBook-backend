"""Đổi điểm lấy voucher."""
from datetime import datetime
from pydantic import BaseModel


class PointRewardOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    reward_type: str = "DISCOUNT_PERCENT"
    icon: str | None = None
    cost_points: int
    discount_percent: float | None = None
    discount_amount: float | None = None
    max_discount: float | None = None
    min_order_amount: float | None = None
    usage_limit: int | None = None
    used_count: int = 0
    valid_days: int
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RedeemRewardOut(BaseModel):
    promotion_id: int
    code: str
    name: str | None = None
    discount_percent: float | None = None
    discount_amount: float | None = None
    free_shipping: bool = False
    max_discount: float | None = None
    min_order_amount: float | None = None
    end_date: datetime | None = None
    points_balance_after: int


class PointRewardCreate(BaseModel):
    name: str
    description: str | None = None
    reward_type: str = "DISCOUNT_PERCENT"
    icon: str | None = None
    cost_points: int
    discount_percent: float | None = None
    discount_amount: float | None = None
    max_discount: float | None = None
    min_order_amount: float | None = None
    usage_limit: int | None = None
    valid_days: int = 30
    active: bool = True


class PointRewardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    reward_type: str | None = None
    icon: str | None = None
    cost_points: int | None = None
    discount_percent: float | None = None
    discount_amount: float | None = None
    max_discount: float | None = None
    min_order_amount: float | None = None
    usage_limit: int | None = None
    used_count: int | None = None
    valid_days: int | None = None
    active: bool | None = None
