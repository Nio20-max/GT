"""Admin routes – manual tick runs, precompute, etc."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/tick/training")
async def run_training_tick():
    """Manually trigger training tick (admin only)."""
    return ok({"message": "training tick executed"})


@router.post("/tick/match")
async def run_match_tick():
    """Manually trigger match simulation (admin only)."""
    return ok({"message": "match tick executed"})


@router.post("/precompute/standings")
async def precompute_standings():
    return ok({"message": "standings precomputed"})


@router.post("/precompute/rankings")
async def precompute_rankings():
    return ok({"message": "rankings precomputed"})
