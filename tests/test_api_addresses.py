"""Test user address book APIs."""
from fastapi.testclient import TestClient


def _current_user(client: TestClient, headers: dict) -> dict:
    r = client.get("/api/v1/users/me", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


def test_address_book_crud_defaults_and_soft_delete(client: TestClient, user_headers):
    user = _current_user(client, user_headers)
    r_profile = client.patch(
        f"/api/v1/users/{user['id']}",
        headers=user_headers,
        json={"phone_number": "0903333333"},
    )
    assert r_profile.status_code == 200, r_profile.text

    r_empty = client.get("/api/v1/addresses/me", headers=user_headers)
    assert r_empty.status_code == 200, r_empty.text
    assert r_empty.json() == []

    r_create = client.post(
        "/api/v1/addresses/me",
        headers=user_headers,
        json={
            "label": "Nha rieng",
            "address_detail": "10 Nguyen Trai",
            "ward": "Ben Thanh",
            "province": "Ho Chi Minh",
        },
    )
    assert r_create.status_code == 201, r_create.text
    first = r_create.json()
    assert first["recipient_name"] == user["full_name"]
    assert first["label"] == "Nha rieng"
    assert first["phone_number"] == "0903333333"
    assert first["is_default"] is True

    r_second = client.post(
        "/api/v1/addresses/me",
        headers=user_headers,
        json={
            "label": "Cong ty",
            "recipient_name": "Receiver Two",
            "phone_number": "0904444444",
            "address_detail": "20 Le Loi",
            "ward": "Ward 2",
            "province": "Ha Noi",
            "is_default": True,
        },
    )
    assert r_second.status_code == 201, r_second.text
    second = r_second.json()
    assert second["is_default"] is True

    r_list = client.get("/api/v1/addresses/me", headers=user_headers)
    assert r_list.status_code == 200, r_list.text
    rows = r_list.json()
    by_id = {row["id"]: row for row in rows}
    assert by_id[first["id"]]["is_default"] is False
    assert by_id[second["id"]]["is_default"] is True

    r_update = client.patch(
        f"/api/v1/addresses/me/{first['id']}",
        headers=user_headers,
        json={"recipient_name": "Receiver One Updated"},
    )
    assert r_update.status_code == 200, r_update.text
    assert r_update.json()["recipient_name"] == "Receiver One Updated"

    r_default = client.patch(
        f"/api/v1/addresses/me/{first['id']}/default",
        headers=user_headers,
    )
    assert r_default.status_code == 200, r_default.text
    assert r_default.json()["is_default"] is True

    r_delete = client.delete(f"/api/v1/addresses/me/{first['id']}", headers=user_headers)
    assert r_delete.status_code == 204, r_delete.text
    r_after = client.get("/api/v1/addresses/me", headers=user_headers)
    assert r_after.status_code == 200, r_after.text
    assert all(row["id"] != first["id"] for row in r_after.json())


def test_address_book_rejects_other_user_address(client: TestClient, auth_headers, user_headers):
    r_create = client.post(
        "/api/v1/addresses/me",
        headers=auth_headers,
        json={
            "label": "Owner address",
            "recipient_name": "Owner",
            "phone_number": "0905555555",
            "address_detail": "Owner House",
            "ward": "Owner Ward",
            "province": "Owner Province",
        },
    )
    assert r_create.status_code == 201, r_create.text
    address_id = r_create.json()["id"]

    r_patch = client.patch(
        f"/api/v1/addresses/me/{address_id}",
        headers=user_headers,
        json={"recipient_name": "Stolen"},
    )
    assert r_patch.status_code == 404

    r_delete = client.delete(f"/api/v1/addresses/me/{address_id}", headers=user_headers)
    assert r_delete.status_code == 404
