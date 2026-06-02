"""Promotion model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Promotion(Base):
    """Bảng promotion."""

    __tablename__ = "promotion"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    code = Column(String(255), nullable=True)
    discount_percent = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    free_shipping = Column(Boolean, nullable=False, default=False)
    end_date = Column(DateTime, nullable=True)
    max_discount = Column(Float, nullable=True)
    name = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    min_order_amount = Column(Float, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, nullable=False, default=0)

    order_promotions = relationship("OrderPromotion", back_populates="promotion")
