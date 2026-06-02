"""Cấu hình đổi điểm lấy voucher."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime

from app.core.database import Base


class PointReward(Base):
    __tablename__ = "point_rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    reward_type = Column(String(32), nullable=False, default="DISCOUNT_PERCENT")
    icon = Column(String(64), nullable=True)
    cost_points = Column(Integer, nullable=False)
    discount_percent = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    max_discount = Column(Float, nullable=True)
    min_order_amount = Column(Float, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, nullable=False, default=0)
    valid_days = Column(Integer, nullable=False, default=30)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
