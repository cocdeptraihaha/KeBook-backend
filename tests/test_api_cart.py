"""Test API cart."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def book_id(client: TestClient, admin_headers):
    """Tạo sách và trả về id."""
    r = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sách giỏ hàng",
            "author": "TG",
            "selling_price": 50000,
            "stock_quantity": 100,
        },
    )
    return r.json()["id"]


def test_get_cart_empty(client: TestClient, auth_headers):
    """Giỏ hàng rỗng."""
    r = client.get("/api/v1/cart/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_add_to_cart(client: TestClient, auth_headers, book_id):
    """Thêm sách vào giỏ."""
    r = client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 2},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["book_id"] == book_id
    assert data["quantity"] == 2


def test_add_to_cart_requires_auth(client: TestClient, book_id):
    """Thêm giỏ cần đăng nhập."""
    r = client.post(
        "/api/v1/cart/",
        json={"book_id": book_id, "quantity": 1},
    )
    assert r.status_code == 401


def test_get_cart_with_items(client: TestClient, auth_headers, book_id):
    """Lấy giỏ có items."""
    client.post("/api/v1/cart/", headers=auth_headers, json={"book_id": book_id, "quantity": 1})
    r = client.get("/api/v1/cart/", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1
