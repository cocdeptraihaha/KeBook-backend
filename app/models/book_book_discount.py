"""Association table between books and book_discounts (many-to-many)."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, func

from app.core.database import Base


class BookBookDiscount(Base):
    """Bảng liên kết book_book_discount (book_id <-> discount_id)."""

    __tablename__ = "book_book_discount"

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    discount_id = Column(Integer, ForeignKey("book_discounts.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

