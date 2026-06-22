"""Schema cho dashboard admin."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DashboardSummaryOut(BaseModel):
    revenue: float
    order_count: int
    aov: float
    new_user_count: int
    low_stock_count: int
    pending_order_count: int


class TopBookRow(BaseModel):
    book_id: int
    title: Optional[str] = None
    quantity_sold: int
    revenue: float


class CategoryRevenueRow(BaseModel):
    category_id: int
    category_name: Optional[str] = None
    revenue: float
    order_count: int


class UserTimeseriesRow(BaseModel):
    period: str
    new_users: int


class TopCustomerOut(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    order_count: int
    total_spent: float


class OrderStatusBreakdownRow(BaseModel):
    status: str
    count: int
    revenue: float


class CancelRatePointOut(BaseModel):
    period: str
    total_orders: int
    cancelled_count: int
    cancel_rate: float


class RevenueTimeseriesRow(BaseModel):
    period: str
    order_count: int
    revenue: float


class BuyerGenderRow(BaseModel):
    gender: str
    user_count: int
    revenue: float
    order_count: int

