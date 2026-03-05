"""Alliance routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/alliances", tags=["alliances"])


@router.get("")
async def list_alliances():
    return ok({"alliances": []})


@router.post("")
async def create_alliance():
    return ok({"message": "alliance created"})


@router.get("/{alliance_id}")
async def get_alliance(alliance_id: str):
    return ok({"alliance_id": alliance_id})


@router.post("/{alliance_id}/join")
async def join_alliance(alliance_id: str):
    return ok({"message": "joined alliance"})
