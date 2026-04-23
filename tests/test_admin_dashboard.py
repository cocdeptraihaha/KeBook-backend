"""Admin dashboard analytics endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_top_customers_requires_admin(client: TestClient, user_headers: dict):
    r = client.get("/api/v1/admin/dashboard/top-customers", headers=user_headers)
    assert r.status_code == 403


def test_top_customers_ok(client: TestClient, admin_headers: dict):
    r = client.get("/api/v1/admin/dashboard/top-customers", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_order_status_breakdown_ok(client: TestClient, admin_headers: dict):
    r = client.get("/api/v1/admin/dashboard/order-status-breakdown", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    statuses = {row["status"] for row in data}
    assert "PENDING" in statuses
    assert "DELIVERED" in statuses


def test_cancellation_timeseries_ok(client: TestClient, admin_headers: dict):
    r = client.get(
        "/api/v1/admin/dashboard/cancellation-timeseries",
        headers=admin_headers,
        params={"group_by": "day"},
    )
    assert r.status_code == 200
    assert r.json() == []
