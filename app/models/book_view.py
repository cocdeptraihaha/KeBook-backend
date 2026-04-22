"""Lịch sử xem sách (để đã xem + đếm lượt xem)."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class BookView(Base):
    __tablename__ = "book_views"
    __table_args__ = (Index("ix_book_views_user_viewed", "user_id", "viewed_at"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="book_views")
    book = relationship("Book", back_populates="book_views")
