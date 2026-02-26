"""Test API auth: register, login, verify-otp."""
import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    """Đăng ký thành công."""
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "Pass123!@#",
            "full_name": "New User",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "newuser@test.com"
    assert "message" in data


def test_resend_otp(client: TestClient):
    """Gửi lại OTP cho user chưa kích hoạt."""
    # Đăng ký trước
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "resend@test.com",
            "username": "resenduser",
            "password": "Pass123!@#",
        },
    )
    r = client.post(
        "/api/v1/auth/resend-otp",
        json={"email": "resend@test.com"},
    )
    assert r.status_code == 200
    assert "message" in r.json()


def test_resend_otp_invalid_email(client: TestClient):
    """Resend OTP với email không tồn tại - vẫn trả 200 (bảo mật)."""
    r = client.post(
        "/api/v1/auth/resend-otp",
        json={"email": "nonexistent@test.com"},
    )
    assert r.status_code == 200
    assert "message" in r.json()


def test_register_duplicate_email(client: TestClient):
    """Đăng ký trùng email."""
    payload = {
        "email": "dup@test.com",
        "username": "user1",
        "password": "Pass123!@#",
    }
    client.post("/api/v1/auth/register", json=payload)
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 400


def test_login_success(client: TestClient, auth_headers):
    """Login sau khi đã verify OTP."""
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "Test123!@#"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_login_wrong_password(client: TestClient, auth_headers):
    """Login sai mật khẩu."""
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "WrongPass"},
    )
    assert r.status_code == 401


def test_me_requires_auth(client: TestClient):
    """GET /users/me cần token."""
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401


def test_me_with_token(client: TestClient, auth_headers):
    """GET /users/me với token hợp lệ."""
    r = client.get("/api/v1/users/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"
