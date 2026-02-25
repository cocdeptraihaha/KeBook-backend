"""OrderStatusHistory model."""
import enum
from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrderHistoryStatus(str, enum.Enum):
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    DELIVERED = "DELIVERED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    RETURNED = "RETURNED"
    SHIPPED = "SHIPPED"


class OrderStatusHistory(Base):
    """Bảng order_status_history."""

    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    e_order_history = Column(SQLEnum(OrderHistoryStatus), nullable=True)
    status_change_date = Column(DateTime, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    order = relationship("Order", back_populates="status_history")
