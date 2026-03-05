"""Task routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
async def list_tasks():
    return ok({"tasks": []})


@router.post("/{task_id}/claim")
async def claim_task(task_id: str):
    return ok({"message": "reward claimed"})
