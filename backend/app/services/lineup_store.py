from __future__ import annotations

from dataclasses import asdict, dataclass
from threading import Lock

from app.core.config import settings
from app.services.persistent_json import JsonStateFile
from app.services.runtime_state import RUNTIME_STATE


@dataclass
class TacticsRecord:
    style: str = "balanced"
    pressing: int = 50
    tempo: int = 50


class LineupStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._state_file = JsonStateFile(settings.state_dir_path / "lineup_state.json")
        self._current_by_user: dict[str, dict] = {}
        self._upcoming_by_user: dict[str, dict[str, dict]] = {}
        self._queue_by_user: dict[str, list[dict]] = {}
        self._tactics_by_user: dict[str, TacticsRecord] = {}
        self._load()

    def _load(self) -> None:
        payload = self._state_file.load(
            default={
                "currentByUser": {},
                "upcomingByUser": {},
                "queueByUser": {},
                "tacticsByUser": {},
            }
        )
        if not isinstance(payload, dict):
            return
        current = payload.get("currentByUser", {})
        upcoming = payload.get("upcomingByUser", {})
        queue = payload.get("queueByUser", {})
        tactics = payload.get("tacticsByUser", {})

        if isinstance(current, dict):
            self._current_by_user = {str(k): v for k, v in current.items() if isinstance(v, dict)}
        if isinstance(upcoming, dict):
            self._upcoming_by_user = {
                str(k): {str(fk): fv for fk, fv in v.items() if isinstance(fv, dict)}
                for k, v in upcoming.items()
                if isinstance(v, dict)
            }
        if isinstance(queue, dict):
            self._queue_by_user = {
                str(k): [item for item in v if isinstance(item, dict)]
                for k, v in queue.items()
                if isinstance(v, list)
            }
        if isinstance(tactics, dict):
            for user_id, raw in tactics.items():
                if not isinstance(raw, dict):
                    continue
                try:
                    self._tactics_by_user[str(user_id)] = TacticsRecord(**raw)
                except Exception:
                    continue

    def _save(self) -> None:
        self._state_file.save(
            {
                "currentByUser": self._current_by_user,
                "upcomingByUser": self._upcoming_by_user,
                "queueByUser": self._queue_by_user,
                "tacticsByUser": {k: asdict(v) for k, v in self._tactics_by_user.items()},
            }
        )

    def current(self, user_id: str) -> dict:
        with self._lock:
            return dict(self._current_by_user.get(user_id, {"formation": "4-4-2", "playerIds": []}))

    def set_current(self, user_id: str, payload: dict) -> dict:
        with self._lock:
            self._current_by_user[user_id] = payload
            self._save()
            return dict(payload)

    def upcoming(self, user_id: str, fixture_id: int) -> dict:
        with self._lock:
            by_fixture = self._upcoming_by_user.setdefault(user_id, {})
            return dict(by_fixture.get(str(fixture_id), {}))

    def set_upcoming(self, user_id: str, fixture_id: int, payload: dict) -> dict:
        with self._lock:
            by_fixture = self._upcoming_by_user.setdefault(user_id, {})
            by_fixture[str(fixture_id)] = payload
            self._save()
            return dict(payload)

    def queue_change(self, user_id: str, fixture_id: int, payload: dict) -> dict:
        with self._lock:
            queue = self._queue_by_user.setdefault(user_id, [])
            item = {"fixtureId": fixture_id, "payload": payload}
            queue.append(item)
            self._save()
            return item

    def queued(self, user_id: str) -> list[dict]:
        with self._lock:
            return list(self._queue_by_user.get(user_id, []))

    def tactics(self, user_id: str) -> TacticsRecord:
        with self._lock:
            return self._tactics_by_user.get(user_id, TacticsRecord())

    def set_tactics(self, user_id: str, tactics: TacticsRecord) -> TacticsRecord:
        with self._lock:
            self._tactics_by_user[user_id] = tactics
            self._save()
            return tactics

    def lock_status(self, fixture_id: int) -> dict:
        return RUNTIME_STATE.fixture_lock_status(fixture_id)


LINEUP_STORE = LineupStore()
