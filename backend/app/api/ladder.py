"""Ladder / ranking routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/ladder", tags=["ladder"])


@router.get("/global")
async def global_ladder():
    return ok({"ladder": []})


@router.get("/league")
async def league_ladder():
    return ok({"ladder": []})


@router.post("/challenge")
async def challenge():
    return ok({"message": "challenge sent"})
