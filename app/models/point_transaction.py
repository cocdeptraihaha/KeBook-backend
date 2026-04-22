"""Lịch sử cộng/trừ điểm tích lũy."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class PointTransaction(Base):
    """Giao dịch điểm (audit trail)."""

    __tablename__ = "point_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    delta = Column(Integer, nullable=False)
    reason = Column(String(64), nullable=False)
    ref_type = Column(String(64), nullable=True)
    ref_id = Column(Integer, nullable=True)
    balance_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="point_transactions")
