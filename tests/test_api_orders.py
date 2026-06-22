"""Test API orders."""
import pytest
from fastapi.testclient import TestClient


def test_get_orders_empty(client: TestClient, empty_cart_headers):
    """Danh sách đơn hàng rỗng (user tách biệt, không dùng chung seed/test khác)."""
    r = client.get("/api/v1/orders/", headers=empty_cart_headers)
    assert r.status_code == 200
    res = r.json()
    assert res["items"] == []


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


def test_checkout_with_saved_address_id(client: TestClient, auth_headers, admin_headers):
    """Checkout with address_id snapshots receiver and full address."""
    r_address = client.post(
        "/api/v1/addresses/me",
        headers=auth_headers,
        json={
            "label": "Nha rieng",
            "recipient_name": "Nguyen Van A",
            "phone_number": "0907777777",
            "address_detail": "99 Tran Hung Dao",
            "ward": "Cau Ong Lanh",
            "province": "Ho Chi Minh",
        },
    )
    assert r_address.status_code == 201, r_address.text
    address_id = r_address.json()["id"]

    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sach checkout address id",
            "author": "T",
            "selling_price": 100000,
            "stock_quantity": 50,
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
        json={"address_id": address_id},
    )
    assert r_checkout.status_code == 201, r_checkout.text
    order = r_checkout.json()["order"]
    assert order["address_id"] == address_id
    assert order["full_name"] == "Nguyen Van A"
    assert order["phone_number"] == "0907777777"
    assert order["shipping_address"] == "99 Tran Hung Dao, Cau Ong Lanh, Ho Chi Minh"


def test_checkout_rejects_other_user_address_id(
    client: TestClient, auth_headers, user_headers, admin_headers
):
    r_address = client.post(
        "/api/v1/addresses/me",
        headers=user_headers,
        json={
            "label": "Dia chi user khac",
            "recipient_name": "Other User",
            "phone_number": "0908888888",
            "address_detail": "Other House",
            "ward": "Other Ward",
            "province": "Other Province",
        },
    )
    assert r_address.status_code == 201, r_address.text
    address_id = r_address.json()["id"]

    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sach reject other address",
            "author": "T",
            "selling_price": 100000,
            "stock_quantity": 50,
        },
    )
    assert r_book.status_code == 201, r_book.text
    book_id = r_book.json()["id"]
    client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 1},
    )

    r_checkout = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={"address_id": address_id},
    )
    assert r_checkout.status_code == 400
    assert "Address not found" in r_checkout.text


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

    # Kiểm tra lại stock của sách tăng lên 20 (ban đầu 20 - 1 checkout + 1 restore = 20)
    r_book_check = client.get(f"/api/v1/books/{book_id}")
    assert r_book_check.status_code == 200
    assert r_book_check.json()["stock_quantity"] == 20


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



def test_vnpay_callback_success(client: TestClient, auth_headers, admin_headers):
    """Test callback VNPAY xử lý thanh toán thành công."""
    # 1. Tạo sách để checkout
    r_book = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sách test VNPAY Callback",
            "author": "VNPAY",
            "selling_price": 50000,
            "stock_quantity": 10,
        },
    )
    assert r_book.status_code == 201
    book_id = r_book.json()["id"]

    # 2. Thêm vào giỏ
    client.post(
        "/api/v1/cart/",
        headers=auth_headers,
        json={"book_id": book_id, "quantity": 1},
    )

    # 3. Checkout chọn VNPAY
    r_co = client.post(
        "/api/v1/orders/checkout",
        headers=auth_headers,
        json={
            "phone_number": "0987654321",
            "shipping_address": "VNPAY Test, HN",
            "payment_method": "VNPAY",
        },
    )
    assert r_co.status_code == 201
    body = r_co.json()
    assert "payment_url" in body

    order_id = body["order"]["id"]

    # 4. Giả lập VNPay callback thành công (ResponseCode = 00)
    # Cần tạo chữ ký đúng chuẩn vnpay
    import hmac
    import hashlib
    import urllib.parse
    from app.core.config import get_settings

    settings = get_settings()
    vnp_hash_secret = settings.VNPAY_HASH_SECRET

    txn_ref = f"{order_id}_20260620000000"
    vnp_params = {
        "vnp_Amount": "5000000",
        "vnp_BankCode": "NCB",
        "vnp_BankTranNo": "VNP12345678",
        "vnp_CardType": "ATM",
        "vnp_OrderInfo": "Thanh toan don hang tai KeBook",
        "vnp_PayDate": "20260620000000",
        "vnp_ResponseCode": "00",
        "vnp_TmnCode": settings.VNPAY_TMN_CODE,
        "vnp_TransactionNo": "20260620111111",
        "vnp_TransactionStatus": "00",
        "vnp_TxnRef": txn_ref,
    }

    sorted_params = sorted(vnp_params.items())
    query_string = urllib.parse.urlencode(sorted_params)
    signature = hmac.new(
        vnp_hash_secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()

    vnp_params["vnp_SecureHash"] = signature

    # 5. Gọi endpoint callback
    r_cb = client.get("/api/v1/orders/payment/vnpay-callback", params=vnp_params)
    assert r_cb.status_code == 200
    assert r_cb.json()["status"] == "SUCCESS"
    assert r_cb.json()["order_id"] == order_id

    # 6. Kiểm tra lại trạng thái đơn hàng -> CONFIRMED
    r_detail = client.get(f"/api/v1/orders/{order_id}", headers=auth_headers)
    assert r_detail.status_code == 200
    assert r_detail.json()["status"] == "CONFIRMED"

