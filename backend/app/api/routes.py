from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.envelope import ok
from app.domain.training import TrainingContext, daily_gain

router = APIRouter(prefix="/api/v1")


class LoginRequest(BaseModel):
    username: str
    password: str


class TrainingPreviewRequest(BaseModel):
    age: int
    strength: float
    talent: int
    style: str
    skill_bucket: str
    fatigue: float = 0.0


@router.post("/auth/login")
def login(payload: LoginRequest) -> dict:
    return ok(
        {
            "token": f"dev-token-{payload.username}",
            "refreshToken": f"dev-refresh-{payload.username}",
            "expiresIn": 3600,
        }
    )


@router.get("/bootstrap")
def bootstrap() -> dict:
    return ok(
        {
            "serverTimeUtc": "2026-03-05T00:00:00Z",
            "features": {
                "league": True,
                "cup": True,
                "ucl": True,
                "transferMarket": True,
                "scouting": True,
            },
        }
    )


@router.get("/club")
def club() -> dict:
    return ok(
        {
            "name": "GT Dev Club",
            "money": 5000000,
            "stars": 20000,
            "leagueId": 1,
            "strength": 100,
        }
    )


@router.post("/training/preview")
def training_preview(payload: TrainingPreviewRequest) -> dict:
    ctx = TrainingContext(
        age=payload.age,
        strength=payload.strength,
        talent=payload.talent,
        style=payload.style,
        skill_bucket=payload.skill_bucket,
        fatigue=payload.fatigue,
    )
    return ok({"dailyGain": round(daily_gain(ctx), 4)})


@router.get("/admin/scheduler/windows")
def scheduler_windows() -> dict:
    return ok(
        {
            "league": {"lock": "17:00", "kickoff": "18:00"},
            "cup_ucl": {"lock": "12:00", "kickoff": "13:00"},
            "friendly": {"lock": "12:00", "kickoff": "13:00"},
            "training_tick": "00:00",
        }
    )
