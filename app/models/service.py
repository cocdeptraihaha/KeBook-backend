"""Service model - dịch vụ vận chuyển."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Service(Base):
    """Bảng service."""

    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    name_service = Column(String(255), nullable=True)
    price = Column(Float, nullable=True)
    status = Column(Boolean, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    orders = relationship("Order", back_populates="service")
