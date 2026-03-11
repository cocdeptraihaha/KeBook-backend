"""OrderItem model."""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrderItem(Base):
    """Bảng order_items."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    book_title = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="order_items")
    order = relationship("Order", back_populates="order_items")
    return_requests = relationship("ReturnRequest", back_populates="order_item")
