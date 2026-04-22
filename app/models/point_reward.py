"""Cấu hình đổi điểm lấy voucher."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime

from app.core.database import Base


class PointReward(Base):
    __tablename__ = "point_rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cost_points = Column(Integer, nullable=False)
    discount_percent = Column(Float, nullable=False)
    max_discount = Column(Float, nullable=True)
    valid_days = Column(Integer, nullable=False, default=30)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
