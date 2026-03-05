from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from app.core.config import settings
from app.services.persistent_json import JsonStateFile


class SchedulerState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._state_file = JsonStateFile(settings.state_dir_path / "scheduler_state.json")
        payload = self._state_file.load(default={"executedWindows": {}})
        if isinstance(payload, dict) and isinstance(payload.get("executedWindows"), dict):
            self._executed_windows = dict(payload["executedWindows"])
        else:
            self._executed_windows: dict[str, dict] = {}

    def _save(self) -> None:
        self._state_file.save({"executedWindows": self._executed_windows})

    def was_executed(self, job_key: str) -> bool:
        with self._lock:
            return job_key in self._executed_windows

    def mark_executed(self, job_key: str, result: dict) -> None:
        with self._lock:
            self._executed_windows[job_key] = {
                "result": result,
                "executedAtUtc": datetime.now(timezone.utc).isoformat(),
            }
            self._save()

    def summary(self) -> dict:
        with self._lock:
            return {
                "executedCount": len(self._executed_windows),
                "latestKeys": list(self._executed_windows.keys())[-10:],
            }


SCHEDULER_STATE = SchedulerState()
