"""Association table: books <-> categories (many-to-many)."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func

from app.core.database import Base


class BookCategory(Base):
    __tablename__ = "book_categories"

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

