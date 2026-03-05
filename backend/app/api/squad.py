"""Squad / player routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/squad", tags=["squad"])


@router.get("")
async def get_squad():
    """Return full squad list."""
    return ok({"players": []})


@router.get("/players/{player_id}")
async def get_player(player_id: UUID):
    """Return single player details."""
    return ok({"player_id": str(player_id), "message": "placeholder"})
