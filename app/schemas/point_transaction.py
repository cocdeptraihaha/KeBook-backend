"""Schemas cho điểm tích lũy."""
from datetime import datetime
from pydantic import BaseModel


class PointTransactionOut(BaseModel):
    id: int
    user_id: int
    delta: int
    reason: str
    ref_type: str | None = None
    ref_id: int | None = None
    balance_after: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LoyaltyBalanceOut(BaseModel):
    balance: int
