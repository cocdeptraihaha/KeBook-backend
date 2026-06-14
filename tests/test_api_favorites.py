"""Test favorites/wishlist APIs."""
from fastapi.testclient import TestClient


def _create_book(client: TestClient, title: str = "Wishlist Book") -> int:
    r = client.post(
        "/api/v1/test/books",
        json={
            "title": title,
            "author": "Wishlist Author",
            "selling_price": 120000,
            "stock_quantity": 5,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_favorites_wishlist_flow(client: TestClient, auth_headers):
    """User can add, list, check, and remove wishlist books."""
    book_id = _create_book(client)

    r = client.post(f"/api/v1/favorites/{book_id}", headers=auth_headers)
    assert r.status_code == 201, r.text
    assert r.json() == {"ok": True}

    # Idempotent add: duplicate wishlist request should stay successful.
    r = client.post(f"/api/v1/favorites/{book_id}", headers=auth_headers)
    assert r.status_code == 201, r.text

    r = client.get("/api/v1/favorites/", headers=auth_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert len([book for book in data if book["id"] == book_id]) == 1
    assert data[0]["id"] == book_id

    r = client.get(
        f"/api/v1/favorites/check?book_ids={book_id},999999",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json() == {str(book_id): True, "999999": False}

    r = client.delete(f"/api/v1/favorites/{book_id}", headers=auth_headers)
    assert r.status_code == 204, r.text

    r = client.get(f"/api/v1/favorites/check?book_ids={book_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json() == {str(book_id): False}


def test_add_favorite_missing_book_returns_404(client: TestClient, auth_headers):
    r = client.post("/api/v1/favorites/999999", headers=auth_headers)
    assert r.status_code == 404
