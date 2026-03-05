"""Scouting routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/scouting", tags=["scouting"])


@router.get("/jobs")
async def list_scouting_jobs():
    return ok({"jobs": []})


@router.post("/jobs")
async def start_scouting_job():
    return ok({"message": "scouting job started"})


@router.get("/results")
async def list_scouting_results():
    return ok({"results": []})
