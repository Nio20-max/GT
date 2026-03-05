"""Training routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/overview")
async def training_overview():
    return ok({"training": {}})


@router.post("/team-style")
async def set_team_style():
    return ok({"message": "team style updated"})


@router.post("/individual")
async def set_individual_training():
    return ok({"message": "individual training updated"})


@router.post("/camp")
async def start_training_camp():
    return ok({"message": "training camp started"})
