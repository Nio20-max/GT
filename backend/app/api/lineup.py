"""Lineup routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/lineup", tags=["lineup"])


@router.get("/current")
async def get_current_lineup():
    return ok({"lineup": []})


@router.put("/current")
async def update_current_lineup():
    return ok({"message": "lineup updated"})


@router.get("/upcoming")
async def get_upcoming_lineup():
    return ok({"lineup": []})
