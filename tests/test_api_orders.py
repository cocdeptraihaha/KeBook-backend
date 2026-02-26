"""Test API orders."""
import pytest
from fastapi.testclient import TestClient


def test_get_orders_empty(client: TestClient, auth_headers):
    """Danh sách đơn hàng rỗng."""
    r = client.get("/api/v1/orders/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_checkout_empty_cart(client: TestClient, empty_cart_headers):
    """Checkout giỏ rỗng."""
    r = client.post(
        "/api/v1/orders/checkout",
        headers=empty_cart_headers,
        json={
            "phone_number": "0901234567",
            "shipping_address": "123 Test St",
        },
    )
    assert r.status_code == 400


def test_checkout_requires_auth(client: TestClient):
    """Checkout cần đăng nhập."""
    r = client.post(
        "/api/v1/orders/checkout",
        json={"shipping_address": "123 Test"},
    )
    assert r.status_code == 401
