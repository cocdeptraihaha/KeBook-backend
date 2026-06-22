"""Application settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment."""

    ENV: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 90
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    
    # Email settings (cho gửi OTP)
    # Gmail: smtp.gmail.com, port 587, dùng App Password
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Email gửi OTP
    SMTP_PASSWORD: str = ""  # App password (không phải password email thường)
    SMTP_FROM_EMAIL: str = ""  # Email hiển thị người gửi
    SMTP_FROM_NAME: str = "KeBook"
    
    # OTP settings
    OTP_EXPIRE_SECONDS: int = 90  # OTP hết hạn sau 90 giây
    OTP_LENGTH: int = 6  # Độ dài OTP (6 số)

    # Cloudinary (upload ảnh). Format: cloudinary://api_key:api_secret@cloud_name
    CLOUDINARY_URL: str = ""
    MYSQL_SSL_CA: str = ""
    MYSQL_SSL_VERIFY: bool = True

    # VNPAY payment settings
    VNPAY_TMN_CODE: str = "DEMO"
    VNPAY_HASH_SECRET: str = "DEMOHASHSECRET"
    VNPAY_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL: str = "http://localhost:5173/payment/vnpay-callback"

    # Điểm tặng khi tạo đánh giá mới (không tặng khi sửa review)
    REVIEW_REWARD_POINTS: int = 10
    # Cửa sổ ngày sau khi giao để được review (GET eligible + POST review)
    REVIEW_WINDOW_DAYS: int = 30
    # Ghi nhận lượt xem: tối thiểu bao nhiêu phút giữa hai lần count cho cùng user+book
    BOOK_VIEW_DEBOUNCE_MINUTES: int = 30
    # Mỗi điểm tích lũy đổi được bao nhiêu VND giảm trên đơn (checkout)
    LOYALTY_POINT_VALUE_VND: float = 1.0
    # Trần % giá trị đơn (sau voucher) có thể trừ bằng điểm
    LOYALTY_MAX_ORDER_POINTS_DISCOUNT_PERCENT: int = 50

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
