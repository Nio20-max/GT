"""Shop routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/shop", tags=["shop"])


@router.get("/catalog")
async def catalog():
    return ok({"items": []})


@router.post("/purchase")
async def purchase():
    return ok({"message": "purchase completed"})


@router.get("/entitlements")
async def entitlements():
    return ok({"entitlements": []})
