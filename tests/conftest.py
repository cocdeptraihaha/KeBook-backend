"""Pytest fixtures cho API tests."""
import os
from pathlib import Path

# Set test env TRƯỚC khi import app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["TESTING"] = "1"

# Xóa SQLite test cũ để create_all tạo lại schema (cột/bảng mới)
_test_db_path = Path(__file__).resolve().parent.parent / "test.db"
if _test_db_path.exists():
    try:
        _test_db_path.unlink()
    except OSError:
        pass

# Clear settings cache
import app.core.config as config_module
if "get_settings" in dir(config_module):
    config_module.get_settings.cache_clear()

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    """Sync TestClient - dùng cho API tests."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client: TestClient):
    """Đăng ký + verify OTP + trả về headers có token. Nếu user đã có thì login."""
    os.environ["TESTING"] = "1"
    email = "test@example.com"
    password = "Test123!@#"

    # Register (có thể đã tồn tại từ test trước)
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": "testuser",
            "password": password,
            "full_name": "Test User",
        },
    )
    if r.status_code == 201:
        # Mới đăng ký: lấy OTP và verify
        r = client.get(f"/api/v1/test/otp?email={email}")
        assert r.status_code == 200
        otp_code = r.json().get("otp_code")
        assert otp_code, "Không lấy được OTP"
        r = client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp_code": otp_code},
        )
        assert r.status_code == 200, r.text
    else:
        # User đã có: thử login, nếu chưa kích hoạt thì verify OTP
        r = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        if r.status_code != 200:
            # Chưa kích hoạt: lấy OTP mới (forgot password hoặc resend)
            r = client.get(f"/api/v1/test/otp?email={email}")
            if r.status_code == 200 and r.json().get("otp_code"):
                otp_code = r.json()["otp_code"]
                r = client.post(
                    "/api/v1/auth/verify-otp",
                    json={"email": email, "otp_code": otp_code},
                )
        assert r.status_code == 200, r.text

    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(client: TestClient):
    """User thường (không phải admin) - dùng cho test requires_admin."""
    email = "user2@example.com"
    password = "Test123!@#"
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": "user2",
            "password": password,
            "full_name": "User Two",
        },
    )
    if r.status_code == 201:
        r = client.get(f"/api/v1/test/otp?email={email}")
        assert r.status_code == 200
        otp_code = r.json().get("otp_code")
        assert otp_code
        r = client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp_code": otp_code},
        )
    else:
        r = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        if r.status_code != 200:
            r = client.get(f"/api/v1/test/otp?email={email}")
            if r.status_code == 200 and r.json().get("otp_code"):
                r = client.post(
                    "/api/v1/auth/verify-otp",
                    json={"email": email, "otp_code": r.json()["otp_code"]},
                )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def empty_cart_headers(client: TestClient):
    """User có giỏ hàng rỗng - dùng cho test checkout empty cart."""
    email = "emptycart@example.com"
    password = "Test123!@#"
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": "emptycart",
            "password": password,
            "full_name": "Empty Cart User",
        },
    )
    if r.status_code == 201:
        r = client.get(f"/api/v1/test/otp?email={email}")
        assert r.status_code == 200
        otp_code = r.json().get("otp_code")
        assert otp_code
        r = client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp_code": otp_code},
        )
    else:
        r = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        if r.status_code != 200:
            r = client.get(f"/api/v1/test/otp?email={email}")
            if r.status_code == 200 and r.json().get("otp_code"):
                r = client.post(
                    "/api/v1/auth/verify-otp",
                    json={"email": email, "otp_code": r.json()["otp_code"]},
                )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client: TestClient, auth_headers):
    """User đã login + set is_superuser."""
    r = client.post("/api/v1/test/make-admin?email=test@example.com")
    assert r.status_code == 200
    return auth_headers
