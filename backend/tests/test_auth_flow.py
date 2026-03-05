from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


def test_register_login_profile_flow() -> None:
    username = f"alice_auth_flow_{uuid4().hex[:8]}"
    password = "pw123456"
    register_resp = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": "alice@example.com", "password": password},
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["ok"] is True
    register_data = register_resp.json()["data"]
    assert register_data["starterSquad"]["count"] >= 16
    assert 66 <= float(register_data["starterSquad"]["averageStrength"]) <= 74

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["token"]

    profile_resp = client.get(
        "/api/v1/me/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile_resp.status_code == 200
    profile = profile_resp.json()["data"]
    assert profile["authenticated"] is True
    assert profile["user"]["username"] == username

    club_resp = client.get(
        "/api/v1/club",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert club_resp.status_code == 200
    club = club_resp.json()["data"]
    assert club["money"] == 5000000
    assert club["stars"] == 20000

    squad_resp = client.get(
        "/api/v1/squad",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert squad_resp.status_code == 200
    squad = squad_resp.json()["data"]
    assert squad["count"] >= 16
    strengths = [float(player["strength"]) for player in squad["players"]]
    avg_strength = sum(strengths) / len(strengths)
    assert 66 <= avg_strength <= 74
