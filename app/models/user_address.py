"""User address book model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserAddress(Base):
    """Saved shipping address for a user."""

    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    label = Column(String(255), nullable=True)
    recipient_name = Column(String(255), nullable=True)
    phone_number = Column(String(255), nullable=True)
    address_detail = Column(String(255), nullable=True)
    ward = Column(String(255), nullable=True)
    province = Column(String(255), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")
