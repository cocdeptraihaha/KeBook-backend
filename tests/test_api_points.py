"""Test loyalty point reward promotion flows."""
from fastapi.testclient import TestClient


def _create_book(client: TestClient, admin_headers: dict, title: str, price: float) -> int:
    r = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": title,
            "author": "Points",
            "selling_price": price,
            "stock_quantity": 20,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _add_points(client: TestClient, admin_headers: dict, auth_headers: dict, delta: int) -> int:
    r_me = client.get("/api/v1/users/me", headers=auth_headers)
    assert r_me.status_code == 200, r_me.text
    user_id = r_me.json()["id"]
    r = client.post(
        f"/api/v1/users/admin/{user_id}/points-adjust",
        headers=admin_headers,
        json={"delta": delta, "reason": "ADMIN_ADJUST"},
    )
    assert r.status_code == 200, r.text
    return user_id


def test_redeem_fixed_discount_reward_and_checkout(
    client: TestClient, auth_headers, admin_headers
):
    _add_points(client, admin_headers, auth_headers, 1000)

    r_reward = client.post(
        "/api/v1/points/admin/rewards",
        headers=admin_headers,
        json={
            "name": "Test fixed 50k",
            "description": "Giam 50k cho don tu 100k",
            "reward_type": "DISCOUNT_AMOUNT",
            "icon": "ticket-percent",
            "cost_points": 500,
            "discount_amount": 50000,
            "min_order_amount": 100000,
            "usage_limit": 10,
            "valid_days": 30,
            "active": True,
        },
    )
    assert r_reward.status_code == 201, r_reward.text
    reward = r_reward.json()
    assert reward["reward_type"] == "DISCOUNT_AMOUNT"
    assert reward["discount_amount"] == 50000
    assert reward["used_count"] == 0

    r_redeem = client.post(
        f"/api/v1/points/rewards/{reward['id']}/redeem",
        headers=auth_headers,
    )
    assert r_redeem.status_code == 200, r_redeem.text
    voucher = r_redeem.json()
    assert voucher["discount_amount"] == 50000
    assert voucher["min_order_amount"] == 100000
    assert voucher["points_balance_after"] >= 0

    r_again = client.post(
        f"/api/v1/points/rewards/{reward['id']}/redeem",
        headers=auth_headers,
    )
    assert r_again.status_code == 400
    assert "da doi" in r_again.text or "đã đổi" in r_again.text

    book_id = _create_book(client, admin_headers, "Sach voucher fixed", 120000)
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
            "promotion_code": voucher["code"],
            "phone_number": "0901234567",
            "shipping_address": "1 Test",
            "ward": "P1",
            "province": "HCM",
        },
    )
    assert r_checkout.status_code == 201, r_checkout.text
    body = r_checkout.json()
    assert body["discount_total"] == 50000
    assert body["total_amount"] == 70000


def test_redeem_free_shipping_reward(client: TestClient, auth_headers, admin_headers):
    _add_points(client, admin_headers, auth_headers, 400)

    r_reward = client.post(
        "/api/v1/points/admin/rewards",
        headers=admin_headers,
        json={
            "name": "Test free ship",
            "description": "Mien phi van chuyen",
            "reward_type": "FREE_SHIPPING",
            "icon": "truck",
            "cost_points": 300,
            "min_order_amount": 300000,
            "usage_limit": 5,
            "valid_days": 30,
            "active": True,
        },
    )
    assert r_reward.status_code == 201, r_reward.text
    reward = r_reward.json()
    assert reward["reward_type"] == "FREE_SHIPPING"

    r_redeem = client.post(
        f"/api/v1/points/rewards/{reward['id']}/redeem",
        headers=auth_headers,
    )
    assert r_redeem.status_code == 200, r_redeem.text
    voucher = r_redeem.json()
    assert voucher["free_shipping"] is True
    assert voucher["discount_amount"] is None
    assert voucher["discount_percent"] is None
