"""Đổi điểm lấy voucher."""
from datetime import datetime
from pydantic import BaseModel


class PointRewardOut(BaseModel):
    id: int
    name: str
    cost_points: int
    discount_percent: float
    max_discount: float | None = None
    valid_days: int
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RedeemRewardOut(BaseModel):
    promotion_id: int
    code: str
    name: str | None = None
    discount_percent: float | None = None
    max_discount: float | None = None
    end_date: datetime | None = None
    points_balance_after: int
