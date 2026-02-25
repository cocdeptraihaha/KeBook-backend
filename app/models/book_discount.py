"""BookDiscount model."""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BookDiscount(Base):
    """Bảng book_discounts."""

    __tablename__ = "book_discounts"

    id = Column(Integer, primary_key=True, index=True)
    discount_amount = Column(Float, nullable=True)
    discount_percent = Column(Float, nullable=True)
    end_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)

    book = relationship("Book", back_populates="discounts")
