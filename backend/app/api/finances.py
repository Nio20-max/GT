"""Finances routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/finances", tags=["finances"])


@router.get("/wallet")
async def get_wallet():
    return ok({"money": 0, "stars": 0})


@router.get("/ledger")
async def get_ledger():
    return ok({"entries": []})
