"""Review model - đánh giá sách."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    """Bảng review."""

    __tablename__ = "review"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), nullable=True)
    create_at = Column(DateTime, nullable=True)
    rate = Column(Integer, nullable=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
