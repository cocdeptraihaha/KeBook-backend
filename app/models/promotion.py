"""Promotion model."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Promotion(Base):
    """Bảng promotion."""

    __tablename__ = "promotion"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(255), nullable=True)
    discount_percent = Column(Float, nullable=True)
    end_date = Column(DateTime, nullable=True)
    max_discount = Column(Float, nullable=True)
    name = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    order_promotions = relationship("OrderPromotion", back_populates="promotion")
