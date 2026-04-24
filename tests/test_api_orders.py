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


def test_checkout_loyalty_points_discount(client: TestClient, auth_headers, admin_headers):
    """Đổi điểm tích lũy khi checkout: response có points_discount_amount và trừ điểm."""
    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sách checkout điểm",
            "author": "T",
            "selling_price": 100000,
            "stock_quantity": 50,
        },
    )
    assert r_book.status_code == 201, r_book.text
    book_id = r_book.json()["id"]

    r_me = client.get("/api/v1/users/me", headers=auth_headers)
    assert r_me.status_code == 200
    me = r_me.json()
    user_id = me["id"]
    points_before = int(me.get("loyalty_points", 0) or 0)

    client.post(
        "/api/v1/users/admin/%s/points-adjust" % user_id,
        headers=admin_headers,
        json={"delta": 500, "reason": "ADMIN_ADJUST"},
    )

    client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 1},
    )

    r_co = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={
            "phone_number": "0909999999",
            "shipping_address": "1 Test St",
            "ward": "P1",
            "province": "HCM",
            "loyalty_points_to_redeem": 200,
        },
    )
    assert r_co.status_code == 201, r_co.text
    body = r_co.json()
    assert body.get("loyalty_points_redeemed") == 200
    assert float(body.get("points_discount_amount", 0)) == 200.0
    assert body.get("total_amount") is not None

    r_me2 = client.get("/api/v1/users/me", headers=auth_headers)
    assert r_me2.status_code == 200
    assert int(r_me2.json().get("loyalty_points", 0)) == points_before + 500 - 200


def test_admin_status_only_allows_next_progress_or_cancel(
    client: TestClient, auth_headers, admin_headers
):
    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sách test tiến trình đơn",
            "author": "Admin",
            "selling_price": 120000,
            "stock_quantity": 20,
        },
    )
    assert r_book.status_code == 201, r_book.text
    book_id = r_book.json()["id"]

    r_cart = client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 1},
    )
    assert r_cart.status_code in (200, 201), r_cart.text

    r_checkout = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={
            "phone_number": "0901111111",
            "shipping_address": "2 Test St",
            "ward": "P2",
            "province": "HCM",
        },
    )
    assert r_checkout.status_code == 201, r_checkout.text
    order_id = r_checkout.json()["order"]["id"]

    r_skip = client.patch(
        f"/api/v1/orders/admin/{order_id}/status",
        headers=admin_headers,
        json={"status": "SHIPPED"},
    )
    assert r_skip.status_code == 400
    assert "kế tiếp" in r_skip.text

    r_next = client.patch(
        f"/api/v1/orders/admin/{order_id}/status",
        headers=admin_headers,
        json={"status": "CONFIRMED"},
    )
    assert r_next.status_code == 200, r_next.text

    r_cancel = client.patch(
        f"/api/v1/orders/admin/{order_id}/status",
        headers=admin_headers,
        json={"status": "CANCELLED"},
    )
    assert r_cancel.status_code == 200, r_cancel.text
    assert r_cancel.json()["status"] == "CANCELLED"


def test_admin_cannot_cancel_delivered_order(
    client: TestClient, auth_headers, admin_headers
):
    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sách test không hủy delivered",
            "author": "Admin",
            "selling_price": 150000,
            "stock_quantity": 20,
        },
    )
    assert r_book.status_code == 201, r_book.text
    book_id = r_book.json()["id"]

    r_cart = client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 1},
    )
    assert r_cart.status_code in (200, 201), r_cart.text

    r_checkout = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={
            "phone_number": "0902222222",
            "shipping_address": "3 Test St",
            "ward": "P3",
            "province": "HCM",
        },
    )
    assert r_checkout.status_code == 201, r_checkout.text
    order_id = r_checkout.json()["order"]["id"]

    for status in ["CONFIRMED", "INPROGRESS", "SHIPPED", "DELIVERED"]:
        r = client.patch(
            f"/api/v1/orders/admin/{order_id}/status",
            headers=admin_headers,
            json={"status": status},
        )
        assert r.status_code == 200, r.text

    r_cancel = client.patch(
        f"/api/v1/orders/admin/{order_id}/status",
        headers=admin_headers,
        json={"status": "CANCELLED"},
    )
    assert r_cancel.status_code == 400
    assert "Không thể hủy đơn" in r_cancel.text


def test_admin_revenue_timeseries_always_14_days_with_zero_fill(
    client: TestClient, admin_headers
):
    r = client.get(
        "/api/v1/orders/admin/revenue-timeseries",
        headers=admin_headers,
        params={"group_by": "day", "to": "2099-01-01"},
    )
    assert r.status_code == 200, r.text
    rows = r.json()
    assert isinstance(rows, list)
    assert len(rows) == 14
    assert rows[0]["period"] == "2098-12-19"
    assert rows[-1]["period"] == "2099-01-01"
    assert all("order_count" in row and "revenue" in row for row in rows)
    assert all(float(row["revenue"]) == 0.0 for row in rows)
