"""SQLAlchemy models."""
from app.models.user import User
from app.models.otp import OTP, OTPType

__all__ = ["User", "OTP", "OTPType"]
