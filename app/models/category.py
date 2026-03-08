"""Category model - danh mục sách (cây)."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    """Bảng categories."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    parent = relationship("Category", remote_side=[id], backref="children")
