"""API tests cho reviews (eligibility, CRUD, public list/avg)."""
from fastapi.testclient import TestClient


def _create_book(client: TestClient, *, title: str = "Sách review test") -> int:
    r = client.post(
        "/api/v1/test/books",
        json={
            "title": title,
            "author": "Tác giả RT",
            "selling_price": 120000,
            "stock_quantity": 20,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _seed(
    client: TestClient,
    *,
    email: str,
    book_id: int,
    order_status: str = "DELIVERED",
    days_since_delivery: int = 0,
):
    r = client.post(
        "/api/v1/test/seed-review-order",
        params={
            "email": email,
            "book_id": book_id,
            "order_status": order_status,
            "days_since_delivery": days_since_delivery,
        },
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_not_eligible_without_purchase(client: TestClient, auth_headers):
    """Chưa mua / chưa giao: không đủ điều kiện, tạo review 400."""
    book_id = _create_book(client, title="Chưa mua")
    r = client.get(
        f"/api/v1/reviews/me/eligible?book_id={book_id}",
        headers=auth_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["eligible"] is False
    assert body["already_reviewed"] is False

    r2 = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 5, "content": "Hay"},
    )
    assert r2.status_code == 400
    assert "Not eligible" in r2.json().get("detail", "")


def test_not_eligible_inprogress(client: TestClient, auth_headers):
    """Đơn INPROGRESS: không trong cửa sổ đánh giá."""
    book_id = _create_book(client, title="Đang xử lý")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="INPROGRESS",
        days_since_delivery=0,
    )
    r = client.get(
        f"/api/v1/reviews/me/eligible?book_id={book_id}",
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["eligible"] is False

    r2 = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 4},
    )
    assert r2.status_code == 400


def test_create_review_delivered_plus_5d(client: TestClient, auth_headers):
    """DELIVERED cách đây 5 ngày: tạo review thành công."""
    book_id = _create_book(client, title="Đã giao 5d")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="DELIVERED",
        days_since_delivery=5,
    )
    r = client.get(
        f"/api/v1/reviews/me/eligible?book_id={book_id}",
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["eligible"] is True

    r2 = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 5, "content": "Rất hay"},
    )
    assert r2.status_code == 201, r2.text
    data = r2.json()
    assert data["book_id"] == book_id
    assert data["rate"] == 5
    assert data["content"] == "Rất hay"


def test_duplicate_review_400(client: TestClient, auth_headers):
    """Đã có review: tạo lần 2 → 400."""
    book_id = _create_book(client, title="Trùng review")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="DELIVERED",
        days_since_delivery=3,
    )
    r1 = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 4, "content": "Lần 1"},
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 3, "content": "Lần 2"},
    )
    assert r2.status_code == 400
    assert "already reviewed" in r2.json().get("detail", "").lower()


def test_outside_40d_not_eligible(client: TestClient, auth_headers):
    """Giao quá 40 ngày (cửa sổ 30 ngày): không đủ điều kiện."""
    book_id = _create_book(client, title="Quá hạn đánh giá")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="DELIVERED",
        days_since_delivery=40,
    )
    r = client.get(
        f"/api/v1/reviews/me/eligible?book_id={book_id}",
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["eligible"] is False

    r2 = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 5},
    )
    assert r2.status_code == 400


def test_me_eligible_and_avg(client: TestClient, auth_headers):
    """Sau khi tạo review: không còn eligible; avg + count đúng."""
    book_id = _create_book(client, title="Avg test")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="DELIVERED",
        days_since_delivery=2,
    )
    assert (
        client.get(
            f"/api/v1/reviews/me/eligible?book_id={book_id}",
            headers=auth_headers,
        ).json()["eligible"]
        is True
    )

    client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 4, "content": "OK"},
    )

    el = client.get(
        f"/api/v1/reviews/me/eligible?book_id={book_id}",
        headers=auth_headers,
    ).json()
    assert el["eligible"] is False
    assert el["already_reviewed"] is True

    avg_r = client.get(f"/api/v1/reviews/book/{book_id}/avg")
    assert avg_r.status_code == 200
    avg_j = avg_r.json()
    assert avg_j["book_id"] == book_id
    assert avg_j["total_reviews"] == 1
    assert float(avg_j["avg_rate"]) == 4.0


def test_get_my_by_book_404_then_200(client: TestClient, auth_headers):
    """Chưa review → 404; sau khi tạo → 200."""
    book_id = _create_book(client, title="404 rồi 200")
    r404 = client.get(
        f"/api/v1/reviews/me/by-book/{book_id}",
        headers=auth_headers,
    )
    assert r404.status_code == 404

    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="DELIVERED",
        days_since_delivery=1,
    )
    client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 5, "content": "Có rồi"},
    )
    r200 = client.get(
        f"/api/v1/reviews/me/by-book/{book_id}",
        headers=auth_headers,
    )
    assert r200.status_code == 200
    assert r200.json()["rate"] == 5


def test_patch_wrong_user_404(client: TestClient, auth_headers, user_headers):
    """User khác PATCH review của người khác → 404."""
    book_id = _create_book(client, title="Patch owner")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="COMPLETED",
        days_since_delivery=4,
    )
    created = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 3, "content": "A"},
    )
    assert created.status_code == 201
    review_id = created.json()["id"]

    bad = client.patch(
        f"/api/v1/reviews/{review_id}",
        headers=user_headers,
        json={"content": "Hack"},
    )
    assert bad.status_code == 404


def test_list_reviews_has_user(client: TestClient, auth_headers):
    """List theo sách có object user (tên)."""
    book_id = _create_book(client, title="List user")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="DELIVERED",
        days_since_delivery=2,
    )
    client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 5, "content": "Public"},
    )
    r = client.get(f"/api/v1/reviews/book/{book_id}?skip=0&limit=10")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    row = items[0]
    assert "user" in row
    assert row["user"] is not None
    assert row["user"].get("full_name") or row["user"].get("username")


def test_delete_review_204(client: TestClient, auth_headers):
    """Xóa review → 204; sau đó GET my by-book 404."""
    book_id = _create_book(client, title="Xóa 204")
    _seed(
        client,
        email="test@example.com",
        book_id=book_id,
        order_status="DELIVERED",
        days_since_delivery=1,
    )
    created = client.post(
        "/api/v1/reviews/",
        headers=auth_headers,
        json={"book_id": book_id, "rate": 2, "content": "Xóa"},
    )
    assert created.status_code == 201
    review_id = created.json()["id"]

    del_r = client.delete(
        f"/api/v1/reviews/{review_id}",
        headers=auth_headers,
    )
    assert del_r.status_code == 204
    assert del_r.content == b""

    after = client.get(
        f"/api/v1/reviews/me/by-book/{book_id}",
        headers=auth_headers,
    )
    assert after.status_code == 404
