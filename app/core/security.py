"""Security: JWT, password hashing (bcrypt 4.3.0)."""
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt

from app.core.config import get_settings

settings = get_settings()
ALGORITHM = "HS256"


def _password_to_bcrypt_input(password: str) -> bytes:
    """Chuyển mật khẩu (độ dài bất kỳ) thành 64 byte để đưa vào bcrypt.
    Bcrypt giới hạn 72 byte; dùng SHA256(plain) → 64 byte, lưu đầy đủ hash.
    """
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return digest.encode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu với hash (bcrypt 4.3.0)."""
    try:
        pwd_bytes = _password_to_bcrypt_input(plain_password)
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash mật khẩu: SHA256(full password) rồi bcrypt → lưu đầy đủ hashed_password (60 ký tự)."""
    pwd_bytes = _password_to_bcrypt_input(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")
