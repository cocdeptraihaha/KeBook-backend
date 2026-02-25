"""UserNotification model - thông báo đã gửi cho user."""
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserNotification(Base):
    """Bảng user_notification - composite PK."""

    __tablename__ = "user_notification"
    __table_args__ = (PrimaryKeyConstraint("notification_id", "user_id"),)

    notification_id = Column(Integer, ForeignKey("notification.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    is_read = Column(Boolean, nullable=True)
    read_at = Column(DateTime, nullable=True)

    notification = relationship("Notification", back_populates="user_notifications")
