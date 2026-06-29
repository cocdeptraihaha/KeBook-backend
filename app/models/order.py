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


class OrderPaymentStatus(str, enum.Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"


class Order(Base):
    """Bảng orders."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=True)
    note = Column(String(255), nullable=True)
    order_date = Column(DateTime, nullable=True)
    phone_number = Column(String(255), nullable=True)
    shipping_address = Column(String(255), nullable=True)
    tracking_number = Column(String(64), nullable=True)
    shipping_provider = Column(String(64), nullable=True)
    status = Column(SQLEnum(OrderStatus), nullable=True)
    payment_status = Column(SQLEnum(OrderPaymentStatus), default=OrderPaymentStatus.UNPAID, nullable=False)
    total_price = Column(Float, nullable=True)
    payment_id = Column(Integer, ForeignKey("payment.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("user_addresses.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    payment = relationship("Payment", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    user = relationship("User", back_populates="orders")
    address = relationship("UserAddress", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    order_promotions = relationship("OrderPromotion", back_populates="order")
    status_history = relationship("OrderStatusHistory", back_populates="order")
    return_requests = relationship("ReturnRequest", back_populates="order")
