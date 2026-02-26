"""Test API books."""
import pytest
from fastapi.testclient import TestClient


def test_list_books_pagination(client: TestClient):
    """Danh sách sách có phân trang."""
    r = client.get("/api/v1/books/")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


def test_list_books_with_query(client: TestClient):
    """Tìm sách với q (phân trang)."""
    r = client.get("/api/v1/books/?q=test")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_book_not_found(client: TestClient):
    """Lấy sách không tồn tại."""
    r = client.get("/api/v1/books/99999")
    assert r.status_code == 404


def test_create_book_requires_admin(client: TestClient, user_headers):
    """Tạo sách cần admin."""
    r = client.post(
        "/api/v1/books/",
        headers=user_headers,
        json={
            "title": "Sách test",
            "author": "Tác giả",
            "selling_price": 100000,
        },
    )
    assert r.status_code == 403


def test_create_book_as_admin(client: TestClient, admin_headers):
    """Admin tạo sách."""
    r = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sách test",
            "author": "Tác giả",
            "selling_price": 100000,
            "stock_quantity": 10,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Sách test"
    assert data["id"] > 0


def test_get_book(client: TestClient, admin_headers):
    """Lấy chi tiết sách."""
    # Tạo sách trước
    cr = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={"title": "Sách A", "author": "TG", "selling_price": 50000},
    )
    book_id = cr.json()["id"]

    r = client.get(f"/api/v1/books/{book_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Sách A"
