from __future__ import annotations

from typing import Any
from uuid import uuid4


def ok(data: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "traceId": str(uuid4()),
    }


def error(code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
        },
        "traceId": str(uuid4()),
    }
