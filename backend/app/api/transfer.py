"""Transfer market routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/transfer", tags=["transfer"])


@router.get("/auctions")
async def list_auctions():
    return ok({"auctions": []})


@router.post("/auctions")
async def create_auction():
    return ok({"message": "auction created"})


@router.post("/bids")
async def place_bid():
    return ok({"message": "bid placed"})


@router.get("/history")
async def transfer_history():
    return ok({"history": []})
