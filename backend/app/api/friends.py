"""Friends routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("")
async def list_friends():
    return ok({"friends": []})


@router.post("/request")
async def send_friend_request():
    return ok({"message": "friend request sent"})


@router.post("/accept")
async def accept_friend_request():
    return ok({"message": "friend request accepted"})
