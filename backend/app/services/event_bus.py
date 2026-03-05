from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock


class EventBus:
    def __init__(self, maxlen: int = 2000) -> None:
        self._lock = Lock()
        self._cursor = 0
        self._events: deque[dict] = deque(maxlen=maxlen)

    def publish(self, event_type: str, payload: dict) -> dict:
        with self._lock:
            self._cursor += 1
            event = {
                "cursor": self._cursor,
                "event": event_type,
                "payload": payload,
                "timestampUtc": datetime.now(timezone.utc).isoformat(),
            }
            self._events.append(event)
            return event

    def events_since(self, cursor: int, max_items: int = 100) -> list[dict]:
        with self._lock:
            rows = [event for event in self._events if int(event.get("cursor", 0)) > cursor]
            return rows[: max(1, min(max_items, 500))]

    def last_cursor(self) -> int:
        with self._lock:
            return self._cursor


EVENT_BUS = EventBus()
