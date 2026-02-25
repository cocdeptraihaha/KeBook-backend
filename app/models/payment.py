"""Payment model."""
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH = "CASH"
    COD = "COD"
    CREDIT_CARD = "CREDIT_CARD"
    VNPAY = "VNPAY"
    SEPAY = "SEPAY"


class Payment(Base):
    """Bảng payment."""

    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=True)
    bank_code = Column(String(255), nullable=True)
    error_message = Column(String(500), nullable=True)
    method = Column(SQLEnum(PaymentMethod), nullable=True)
    pay_date = Column(DateTime, nullable=True)
    payment_status = Column(String(255), nullable=True)
    vnp_transaction_no = Column(String(255), nullable=True)
    vnp_txn_ref = Column(String(255), nullable=True)

    orders = relationship("Order", back_populates="payment")
