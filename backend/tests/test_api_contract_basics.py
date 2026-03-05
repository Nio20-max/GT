from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def assert_envelope(payload: dict) -> None:
    assert payload["ok"] is True
    assert "traceId" in payload


def test_login_contract() -> None:
    response = client.post("/api/v1/auth/login", json={"username": "alice", "password": "pw"})
    assert response.status_code == 200
    payload = response.json()
    assert_envelope(payload)
    assert "token" in payload["data"]


def test_bootstrap_contract() -> None:
    response = client.get("/api/v1/bootstrap")
    assert response.status_code == 200
    payload = response.json()
    assert_envelope(payload)
    assert payload["data"]["features"]["league"] is True


def test_training_preview_contract() -> None:
    response = client.post(
        "/api/v1/training/preview",
        json={
            "age": 24,
            "strength": 420,
            "talent": 7,
            "style": "balanced",
            "skill_bucket": "midfield",
            "fatigue": 20,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert_envelope(payload)
    assert payload["data"]["dailyGain"] > 0


def test_scheduler_window_contract() -> None:
    response = client.get("/api/v1/admin/scheduler/windows")
    assert response.status_code == 200
    payload = response.json()
    assert_envelope(payload)
    assert payload["data"]["league"]["lock"] == "17:00"
