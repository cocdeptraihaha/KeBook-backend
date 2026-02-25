"""OrderPromotion model - khuyến mãi áp dụng cho đơn hàng."""
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrderPromotion(Base):
    """Bảng order_promotion."""

    __tablename__ = "order_promotion"

    id = Column(Integer, primary_key=True, index=True)
    discount_amount = Column(Float, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    promotion_id = Column(Integer, ForeignKey("promotion.id"), nullable=True)

    order = relationship("Order", back_populates="order_promotions")
    promotion = relationship("Promotion", back_populates="order_promotions")
