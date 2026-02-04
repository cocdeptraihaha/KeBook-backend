"""OTP model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from datetime import datetime, timedelta
import enum
from app.core.database import Base


class OTPType(str, enum.Enum):
    """Loại OTP."""
    ACTIVATION = "activation"  # Kích hoạt tài khoản
    RESET_PASSWORD = "reset_password"  # Reset mật khẩu


class OTP(Base):
    """OTP codes table."""

    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    code = Column(String(6), nullable=False)  # 6 số
    otp_type = Column(SQLEnum(OTPType), nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_expired(self) -> bool:
        """Kiểm tra OTP đã hết hạn chưa."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Kiểm tra OTP còn hợp lệ không."""
        return not self.is_used and not self.is_expired()
