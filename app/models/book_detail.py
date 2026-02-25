"""BookDetail model - thông tin chi tiết sách."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class BookDetail(Base):
    """Bảng book_details."""

    __tablename__ = "book_details"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=True)
    height = Column(Float, nullable=True)
    image_url = Column(String(255), nullable=True)
    length = Column(Float, nullable=True)
    pages = Column(Integer, nullable=True)
    publisher = Column(String(255), nullable=True)
    supplier = Column(String(255), nullable=True)
    weight = Column(Float, nullable=True)
    width = Column(Float, nullable=True)

    book = relationship("Book", back_populates="book_detail", uselist=False)
