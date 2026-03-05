"""Bootstrap / HUD / runtime-calendar routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import ok

router = APIRouter(tags=["bootstrap"])


@router.get("/bootstrap")
async def bootstrap():
    """Return initial client payload after login."""
    return ok({
        "league_size": settings.league_size,
        "starting_money": settings.starting_money,
        "starting_stars": settings.starting_stars,
    })


@router.get("/hud/resources")
async def hud_resources():
    """Return current HUD resource bar data."""
    # TODO: fetch from DB for the authenticated user
    return ok({"money": 0, "stars": 0})


@router.get("/runtime/calendar")
async def runtime_calendar():
    """Return upcoming schedule events."""
    return ok({
        "league_kickoff_utc": settings.league_kickoff_utc,
        "league_lock_utc": settings.league_lock_utc,
        "cup_kickoff_utc": settings.cup_kickoff_utc,
        "cup_lock_utc": settings.cup_lock_utc,
        "training_tick_utc": settings.training_tick_utc,
    })
