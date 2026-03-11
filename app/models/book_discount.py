"""BookDiscount model."""
from sqlalchemy import Column, Integer, Float, DateTime
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

    books = relationship(
        "Book",
        secondary="book_book_discount",
        back_populates="discounts",
    )
