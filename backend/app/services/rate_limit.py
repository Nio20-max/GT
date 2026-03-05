from __future__ import annotations

import time
from collections import deque
from threading import Lock


class RateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._history: dict[str, deque[float]] = {}

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        with self._lock:
            queue = self._history.setdefault(key, deque())
            while queue and queue[0] <= now - window_seconds:
                queue.popleft()
            if len(queue) >= limit:
                return False
            queue.append(now)
            return True


RATE_LIMITER = RateLimiter()
