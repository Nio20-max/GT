"""League routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/league", tags=["league"])


@router.get("/standings")
async def standings():
    return ok({"standings": []})


@router.get("/fixtures")
async def fixtures():
    return ok({"fixtures": []})


@router.get("/results")
async def results():
    return ok({"results": []})
