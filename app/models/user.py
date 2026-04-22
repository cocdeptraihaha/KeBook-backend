"""User model - khớp với database kebookdb."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User table - profile + auth fields."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Profile
    full_name = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    province = Column(String(255), nullable=True)
    ward = Column(String(255), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(255), nullable=True)
    phone_number = Column(String(255), nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # soft delete
    # Auth
    email = Column(String(255), unique=True, index=True, nullable=True)
    username = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    loyalty_points = Column(Integer, nullable=False, default=0)

    # Relationships
    cart_items = relationship("Cart", back_populates="user", foreign_keys="Cart.user_id")
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")
    reviews = relationship("Review", back_populates="user", foreign_keys="Review.user_id")
    point_transactions = relationship(
        "PointTransaction", back_populates="user", foreign_keys="PointTransaction.user_id"
    )
    favorites = relationship("Favorite", back_populates="user", foreign_keys="Favorite.user_id")
    book_views = relationship("BookView", back_populates="user", foreign_keys="BookView.user_id")
