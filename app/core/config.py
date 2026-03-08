"""Application settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    SECRET_KEY: str = "keynaykhongaibiet"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 90
    API_V1_STR: str = "/api/v1"
    
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

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
