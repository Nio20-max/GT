"""Club routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/club", tags=["club"])


@router.get("")
async def get_club():
    """Get current user's club."""
    # TODO: fetch club from DB
    return ok({"message": "club data placeholder"})


@router.patch("")
async def update_club():
    """Update club details."""
    return ok({"message": "club updated"})


@router.get("/accomplishments")
async def get_accomplishments():
    return ok({"accomplishments": []})


@router.get("/sponsors")
async def get_sponsors():
    return ok({"sponsors": []})
