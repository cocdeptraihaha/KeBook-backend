"""Admin return-requests list."""
import pytest
from fastapi.testclient import TestClient


def test_admin_return_list_requires_admin(client: TestClient, user_headers: dict):
    r = client.get("/api/v1/return-requests/admin/all", headers=user_headers)
    assert r.status_code == 403


def test_admin_return_list_ok(client: TestClient, admin_headers: dict):
    r = client.get("/api/v1/return-requests/admin/all", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []
