"""Notification model."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notification(Base):
    """Bảng notification."""

    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(255), nullable=True)
    send_date = Column(DateTime, nullable=True)
    title = Column(String(255), nullable=True)
    type = Column(String(255), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    user_notifications = relationship("UserNotification", back_populates="notification")
