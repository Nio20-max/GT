"""Shared response envelopes."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    model_config = {"from_attributes": True}

    ok: bool = True
    data: T | None = None
    error: dict[str, Any] | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = {"from_attributes": True}

    ok: bool = True
    data: list[T] = []
    total: int = 0
    page: int = 1
    per_page: int = 20


def ok(data: Any = None) -> dict:
    return {"ok": True, "data": data}


def err(code: str, message: str, status: int = 400) -> dict:
    return {"ok": False, "error": {"code": code, "message": message}}
