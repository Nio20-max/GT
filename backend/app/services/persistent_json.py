from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from threading import Lock
from typing import Any


class JsonStateFile:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, default: Any) -> Any:
        with self._lock:
            if not self._path.exists():
                return default
            try:
                with self._path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)
            except Exception:
                return default

    def save(self, payload: Any) -> None:
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(prefix="gt-state-", suffix=".tmp", dir=str(self._path.parent))
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, ensure_ascii=True, separators=(",", ":"))
                os.replace(tmp_path, self._path)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
