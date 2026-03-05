"""Stadium routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/stadium", tags=["stadium"])


@router.get("")
async def get_stadium():
    return ok({"stadium": {}})


@router.post("/upgrade")
async def upgrade_stadium():
    return ok({"message": "upgrade started"})
