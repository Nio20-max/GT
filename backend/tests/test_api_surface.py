from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)

SAMPLE_ENDPOINTS = [
    ("post", "/api/v1/auth/register"),
    ("get", "/api/v1/me/profile"),
    ("get", "/api/v1/hud/resources"),
    ("get", "/api/v1/runtime/calendar"),
    ("get", "/api/v1/club/accomplishments"),
    ("post", "/api/v1/sponsors/1/accept"),
    ("get", "/api/v1/finances/history?days=30"),
    ("post", "/api/v1/stadium/buildings/1/upgrade"),
    ("get", "/api/v1/players/1"),
    ("post", "/api/v1/players/1/skill-cards/apply"),
    ("put", "/api/v1/lineup/current"),
    ("post", "/api/v1/training/team"),
    ("get", "/api/v1/scouting/results"),
    ("post", "/api/v1/transfer/auctions/1/bid"),
    ("get", "/api/v1/league/table"),
    ("get", "/api/v1/matches/1/live"),
    ("get", "/api/v1/ucl/fixtures"),
    ("post", "/api/v1/ladder/stamina/refill"),
    ("post", "/api/v1/friends/search"),
    ("get", "/api/v1/chat/channels"),
    ("post", "/api/v1/shop/offers/1/grant"),
    ("post", "/api/v1/equipment/shirts/1/buy"),
    ("post", "/api/v1/alliances/1/join-request"),
    ("post", "/api/v1/tasks/1/claim"),
    ("post", "/api/v1/admin/ticks/run"),
]


def test_api_surface_endpoints_registered() -> None:
    register_payload = {
        "username": f"surface_{uuid4().hex[:8]}",
        "email": "surface@example.com",
        "password": "surfacepass1",
    }

    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": register_payload["username"], "password": register_payload["password"]},
    )
    token = login_resp.json()["data"]["token"]
    auth_headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": "surface-1"}

    squad_resp = client.get("/api/v1/squad", headers=auth_headers)
    assert squad_resp.status_code == 200
    first_player_id = squad_resp.json()["data"]["players"][0]["player_id"]

    for method, url in SAMPLE_ENDPOINTS:
        request_fn = getattr(client, method)
        body = {}
        if url == "/api/v1/auth/register":
            continue
        if "/players/1" in url:
            url = url.replace("/players/1", f"/players/{first_player_id}")
        if url == "/api/v1/lineup/current":
            body = {"formation": "4-4-2", "playerIds": []}
        if url == "/api/v1/training/team":
            body = {"style": "balanced", "intensity": 50}
        if url == "/api/v1/friends/search":
            body = {"query": "test"}
        if url == "/api/v1/transfer/auctions/1/bid":
            body = {"amount": 100000}
        if method == "get":
            response = request_fn(url, headers=auth_headers)
        else:
            response = request_fn(url, json=body, headers=auth_headers)
        expected_status = 201 if url == "/api/v1/auth/register" else 200
        assert response.status_code == expected_status, f"{method.upper()} {url} failed"
        payload = response.json()
        assert payload["ok"] is True
        assert "traceId" in payload


def test_realtime_websocket_connects() -> None:
    with client.websocket_connect("/api/v1/realtime") as ws:
        message = ws.receive_json()
        assert message["ok"] is True
        assert "topics" in message["data"]
