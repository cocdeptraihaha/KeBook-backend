"""Test API categories."""
import pytest
from fastapi.testclient import TestClient


def test_list_categories(client: TestClient):
    """Danh sách danh mục."""
    r = client.get("/api/v1/categories/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_root_categories(client: TestClient):
    """Danh mục gốc."""
    r = client.get("/api/v1/categories/roots")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_category_requires_admin(client: TestClient, user_headers):
    """Tạo danh mục cần admin."""
    r = client.post(
        "/api/v1/categories/",
        headers=user_headers,
        json={"name": "Danh mục test"},
    )
    assert r.status_code == 403


def test_create_category_as_admin(client: TestClient, admin_headers):
    """Admin tạo danh mục."""
    r = client.post(
        "/api/v1/categories/",
        headers=admin_headers,
        json={"name": "Sách văn học"},
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Sách văn học"
