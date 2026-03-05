from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    username = f"ops_{uuid4().hex[:8]}"
    password = "opspassword1"
    register = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert register.status_code == 201
    login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_shop_grant_idempotent() -> None:
    headers = _auth_headers()
    headers_with_idem = {**headers, "Idempotency-Key": "idem-ops-1"}

    first = client.post("/api/v1/shop/offers/1/grant", headers=headers_with_idem, json={})
    second = client.post("/api/v1/shop/offers/1/grant", headers=headers_with_idem, json={})
    assert first.status_code == 200
    assert second.status_code == 200

    first_data = first.json()["data"]
    second_data = second.json()["data"]
    assert first_data["entry"]["entryId"] == second_data["entry"]["entryId"]


def test_runtime_metrics_and_settlements_endpoints() -> None:
    precompute = client.post("/api/v1/admin/precompute/run", params={"competition": "league"})
    assert precompute.status_code == 200
    publish = client.post("/api/v1/admin/ticks/run")
    assert publish.status_code == 200

    metrics = client.get("/api/v1/admin/metrics/runtime")
    assert metrics.status_code == 200
    payload = metrics.json()["data"]
    assert "scheduler" in payload
    assert "eventBus" in payload
    assert "settlements" in payload

    settlements = client.get("/api/v1/admin/settlements")
    assert settlements.status_code == 200
    rows = settlements.json()["data"]["records"]
    assert isinstance(rows, list)
