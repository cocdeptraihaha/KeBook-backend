"""Admin dashboard analytics endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_top_customers_requires_admin(client: TestClient, user_headers: dict):
    r = client.get("/api/v1/admin/dashboard/top-customers", headers=user_headers)
    assert r.status_code == 403


def test_top_customers_ok(client: TestClient, admin_headers: dict):
    r = client.get("/api/v1/admin/dashboard/top-customers", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for row in data:
        assert set(row.keys()) >= {"email", "full_name", "order_count", "total_spent"}


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
        params={"group_by": "day", "to": "2099-01-01"},
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 14
    assert rows[0]["period"] == "2098-12-19"
    assert rows[-1]["period"] == "2099-01-01"
    assert all(float(x["cancel_rate"]) == 0.0 for x in rows)


def test_user_timeseries_always_14_days(client: TestClient, admin_headers: dict):
    r = client.get(
        "/api/v1/admin/dashboard/user-timeseries",
        headers=admin_headers,
        params={"group_by": "day", "to": "2099-01-01"},
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 14
    assert rows[0]["period"] == "2098-12-19"
    assert rows[-1]["period"] == "2099-01-01"
