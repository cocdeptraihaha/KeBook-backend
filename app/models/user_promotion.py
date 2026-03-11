"""UserPromotion model - tracking which users have used which promotions."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserPromotion(Base):
    """Bảng user_promotion - lưu trữ user đã sử dụng mã giảm giá."""

    __tablename__ = "user_promotion"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    promotion_id = Column(Integer, ForeignKey("promotion.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    used_at = Column(DateTime, nullable=False)

    user = relationship("User")
    promotion = relationship("Promotion")
    order = relationship("Order")
