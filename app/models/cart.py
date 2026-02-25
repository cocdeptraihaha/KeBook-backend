"""Cart model - giỏ hàng."""
from sqlalchemy import Column, Integer, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cart(Base):
    """Bảng cart."""

    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    create_at = Column(Date, nullable=True)
    quantity = Column(Integer, nullable=True)
    update_at = Column(Date, nullable=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="cart_items")
    user = relationship("User", back_populates="cart_items")
