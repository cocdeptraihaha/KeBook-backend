"""ReturnRequest model - yêu cầu trả hàng."""
import enum
from sqlalchemy import Column, Integer, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReturnRequestStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class ReturnRequest(Base):
    """Bảng return_requests."""

    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    processed_date = Column(DateTime, nullable=True)
    quantity = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    request_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ReturnRequestStatus), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    order = relationship("Order", back_populates="return_requests")
    order_item = relationship("OrderItem", back_populates="return_requests")
