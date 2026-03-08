"""Book model."""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Book(Base):
    """Bảng books."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    edition = Column(Integer, nullable=True)
    publication_date = Column(Date, nullable=True)
    selling_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, nullable=True)
    title = Column(String(255), nullable=True)
    book_detail_id = Column(Integer, ForeignKey("book_details.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    book_detail = relationship("BookDetail", back_populates="book")
    discounts = relationship("BookDiscount", back_populates="book")
    cart_items = relationship("Cart", back_populates="book")
    order_items = relationship("OrderItem", back_populates="book")
    reviews = relationship("Review", back_populates="book")
