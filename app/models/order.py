"""Order model."""
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    CANCELLED = "CANCELLED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    COMPLETED = "COMPLETED"
    CONFIRMED = "CONFIRMED"
    DELIVERED = "DELIVERED"
    INPROGRESS = "INPROGRESS"
    PENDING = "PENDING"
    RETURNED = "RETURNED"
    SHIPPED = "SHIPPED"


class Order(Base):
    """Bảng orders."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=True)
    note = Column(String(255), nullable=True)
    order_date = Column(DateTime, nullable=True)
    phone_number = Column(String(255), nullable=True)
    shipping_address = Column(String(255), nullable=True)
    status = Column(SQLEnum(OrderStatus), nullable=True)
    total_price = Column(Float, nullable=True)
    payment_id = Column(Integer, ForeignKey("payment.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    payment = relationship("Payment", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    order_promotions = relationship("OrderPromotion", back_populates="order")
    status_history = relationship("OrderStatusHistory", back_populates="order")
    return_requests = relationship("ReturnRequest", back_populates="order")
