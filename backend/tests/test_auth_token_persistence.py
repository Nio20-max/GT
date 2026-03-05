from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.services.auth_store import AUTH_STORE


client = TestClient(app)


def test_token_still_valid_after_in_memory_cache_drop() -> None:
    username = f"persist_{uuid4().hex[:8]}"
    password = "persistpw1"

    register = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert register.status_code == 201

    login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json()["data"]["token"]

    # Simulate another process that doesn't have the in-memory token cache.
    AUTH_STORE._tokens.clear()  # type: ignore[attr-defined]

    profile = client.get("/api/v1/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    payload = profile.json()["data"]
    assert payload["authenticated"] is True
    assert payload["user"]["username"] == username
