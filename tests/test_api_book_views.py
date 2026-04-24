"""Book view debounce (MVP)."""
from fastapi.testclient import TestClient


def test_book_view_debounced(client: TestClient, auth_headers, admin_headers):
    r = client.post(
        "/api/v1/books/",
        headers=admin_headers,
        json={
            "title": "Sách view debounce",
            "author": "A",
            "selling_price": 10000,
            "stock_quantity": 10,
        },
    )
    assert r.status_code == 201
    book_id = r.json()["id"]

    def view_count():
        g = client.get(f"/api/v1/books/{book_id}")
        assert g.status_code == 200
        return int(g.json().get("view_count", 0))

    v0 = view_count()
    r1 = client.post(f"/api/v1/books/{book_id}/view", headers=auth_headers)
    assert r1.status_code == 204
    v1 = view_count()
    assert v1 >= v0 + 1

    r2 = client.post(f"/api/v1/books/{book_id}/view", headers=auth_headers)
    assert r2.status_code == 204
    v2 = view_count()
    assert v2 == v1
