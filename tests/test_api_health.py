"""Test health check."""
import pytest
from fastapi.testclient import TestClient


def test_root(client: TestClient):
    """Health check root."""
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_kaith_healthcheck(client: TestClient):
    """Health check Leapcell."""
    r = client.get("/kaithhealthcheck")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
