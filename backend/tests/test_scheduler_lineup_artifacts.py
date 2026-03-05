from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.workers.scheduler import run_due_jobs


client = TestClient(app)


def _auth_header() -> dict[str, str]:
    username = f"lineup_{uuid4().hex[:8]}"
    password = "lineuppw1"
    register = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert register.status_code == 201
    login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_scheduler_windows_idempotent() -> None:
    first = None
    second = None
    for day in range(1, 28):
        now = datetime(2099, 1, day, 18, 5, tzinfo=timezone.utc)
        first = run_due_jobs(now)
        if len(first["executions"]) >= 1:
            second = run_due_jobs(now)
            break
    assert first is not None
    assert second is not None
    assert len(first["executions"]) >= 1
    assert len(second["executions"]) == 0


def test_lineup_lock_and_queue_behavior() -> None:
    headers = _auth_header()
    client.post("/api/v1/admin/seasons/rollover")

    fixtures_resp = client.get("/api/v1/lineup/upcoming", headers=headers)
    assert fixtures_resp.status_code == 200
    fixtures = fixtures_resp.json()["data"]["fixtures"]
    assert len(fixtures) >= 1
    fixture_id = int(fixtures[0]["fixtureId"])

    direct_set = client.put(
        f"/api/v1/lineup/upcoming/{fixture_id}",
        headers=headers,
        json={"formation": "4-3-3", "playerIds": []},
    )
    assert direct_set.status_code == 200
    assert direct_set.json()["data"]["queued"] is False

    client.post("/api/v1/admin/precompute/run", params={"competition": "league"})

    queued_set = client.put(
        f"/api/v1/lineup/upcoming/{fixture_id}",
        headers=headers,
        json={"formation": "3-5-2", "playerIds": []},
    )
    assert queued_set.status_code == 200
    assert queued_set.json()["data"]["queued"] is True


def test_precompute_artifacts_endpoint() -> None:
    client.post("/api/v1/admin/precompute/run", params={"competition": "cup"})
    health = client.get("/api/v1/admin/health/deep")
    sample = health.json()["data"]["sampleFixtures"]
    cup_fixture = next((row for row in sample if row["competition"] == "cup"), None)
    if cup_fixture is None:
        return

    artifact = client.get(f"/api/v1/admin/precompute/artifacts/{cup_fixture['fixture_id']}")
    assert artifact.status_code == 200
    payload = artifact.json()["data"]
    assert payload["fixtureId"] == cup_fixture["fixture_id"]
    assert "checksum" in payload
