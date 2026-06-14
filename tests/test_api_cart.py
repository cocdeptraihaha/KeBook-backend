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


def test_add_to_cart_rejects_quantity_over_stock(client: TestClient, auth_headers, admin_headers):
    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sach stock 5",
            "author": "TG",
            "selling_price": 50000,
            "stock_quantity": 5,
        },
    )
    assert r_book.status_code == 201, r_book.text
    book_id = r_book.json()["id"]

    r = client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 6},
    )
    assert r.status_code == 400
    assert "available stock (5)" in r.text


def test_add_to_cart_rejects_total_quantity_over_stock(client: TestClient, auth_headers, admin_headers):
    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sach stock 5 total",
            "author": "TG",
            "selling_price": 50000,
            "stock_quantity": 5,
        },
    )
    assert r_book.status_code == 201, r_book.text
    book_id = r_book.json()["id"]

    r_first = client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 3},
    )
    assert r_first.status_code == 201, r_first.text

    r_second = client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 3},
    )
    assert r_second.status_code == 400
    assert "available stock (5)" in r_second.text


def test_update_cart_rejects_invalid_or_over_stock(client: TestClient, auth_headers, admin_headers):
    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sach stock 5 update",
            "author": "TG",
            "selling_price": 50000,
            "stock_quantity": 5,
        },
    )
    assert r_book.status_code == 201, r_book.text
    book_id = r_book.json()["id"]

    r_add = client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 2},
    )
    assert r_add.status_code == 201, r_add.text
    cart_id = r_add.json()["id"]

    r_zero = client.patch(
        f"/api/v1/cart/{cart_id}",
        headers=auth_headers,
        json={"quantity": 0},
    )
    assert r_zero.status_code == 400
    assert "Quantity must be positive" in r_zero.text

    r_over = client.patch(
        f"/api/v1/cart/{cart_id}",
        headers=auth_headers,
        json={"quantity": 6},
    )
    assert r_over.status_code == 400
    assert "available stock (5)" in r_over.text
