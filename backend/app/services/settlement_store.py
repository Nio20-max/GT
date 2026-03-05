from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from app.core.config import settings
from app.services.pg_repo import pg_cursor, pg_enabled
from app.services.persistent_json import JsonStateFile


class SettlementStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._state_file = JsonStateFile(settings.state_dir_path / "settlement_state.json")
        payload = self._state_file.load(default={"records": []})
        if isinstance(payload, dict) and isinstance(payload.get("records"), list):
            self._records = [row for row in payload["records"] if isinstance(row, dict)]
        else:
            self._records: list[dict] = []

    def _save(self) -> None:
        if pg_enabled():
            return
        self._state_file.save({"records": self._records})

    def record_fixture_settlement(self, fixture: dict, source: str) -> dict:
        with self._lock:
            row = {
                "settlementId": str(uuid4()),
                "fixtureId": fixture.get("fixtureId"),
                "competition": fixture.get("competition"),
                "seasonId": fixture.get("seasonId"),
                "homeClubId": fixture.get("homeClubId"),
                "awayClubId": fixture.get("awayClubId"),
                "homeGoals": fixture.get("homeGoals"),
                "awayGoals": fixture.get("awayGoals"),
                "source": source,
                "recordedAtUtc": datetime.now(timezone.utc).isoformat(),
            }
            self._records.append(row)
            if pg_enabled():
                try:
                    with pg_cursor() as cur:
                        cur.execute(
                            "INSERT INTO match_settlements (fixture_id, competition, season_id, home_club_id, away_club_id, home_goals, away_goals, source, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())",
                            (
                                row["fixtureId"],
                                row["competition"],
                                row["seasonId"],
                                row["homeClubId"],
                                row["awayClubId"],
                                row["homeGoals"],
                                row["awayGoals"],
                                row["source"],
                            ),
                        )
                except Exception:
                    pass
            self._save()
            return row

    def latest(self, limit: int = 100) -> list[dict]:
        with self._lock:
            return self._records[-max(1, min(limit, 500)) :]


SETTLEMENT_STORE = SettlementStore()
