"""Chat routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/channels")
async def list_channels():
    return ok({"channels": []})


@router.get("/channels/{channel_id}/messages")
async def get_messages(channel_id: str):
    return ok({"messages": []})


@router.post("/channels/{channel_id}/messages")
async def send_message(channel_id: str):
    return ok({"message": "sent"})
