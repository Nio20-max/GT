from __future__ import annotations

from fastapi import APIRouter, Request, WebSocket
from pydantic import BaseModel

from app.api.envelope import ok
from app.domain.training import TrainingContext, daily_gain
from app.services.runtime_state import RUNTIME_STATE

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


CONTRACT_ENDPOINTS: list[tuple[str, str]] = [
    ("POST", "/auth/register"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
    ("GET", "/me/profile"),
    ("PATCH", "/me/profile"),
    ("GET", "/me/settings"),
    ("PATCH", "/me/settings"),
    ("GET", "/hud/resources"),
    ("GET", "/notifications/unread-count"),
    ("GET", "/runtime/calendar"),
    ("GET", "/runtime/locks"),
    ("PATCH", "/club/name"),
    ("GET", "/club/accomplishments"),
    ("GET", "/club/fans-members"),
    ("GET", "/club/season-history"),
    ("GET", "/club/all-time-tables"),
    ("GET", "/sponsors/offers"),
    ("POST", "/sponsors/{offerId}/accept"),
    ("GET", "/emails"),
    ("GET", "/emails/{emailId}"),
    ("POST", "/emails/{emailId}/read"),
    ("DELETE", "/emails/{emailId}"),
    ("GET", "/finances/summary"),
    ("GET", "/finances/history"),
    ("GET", "/finances/ledger"),
    ("GET", "/finances/stars-history"),
    ("GET", "/stadium"),
    ("GET", "/stadium/buildings"),
    ("POST", "/stadium/buildings/{buildingId}/upgrade"),
    ("POST", "/stadium/buildings/{buildingId}/speedup"),
    ("POST", "/stadium/buildings/{buildingId}/deconstruct"),
    ("GET", "/stadium/seats/pricing"),
    ("GET", "/squad"),
    ("GET", "/players/{playerId}"),
    ("POST", "/players/{playerId}/skill-cards/apply"),
    ("POST", "/players/{playerId}/upgrade"),
    ("POST", "/players/{playerId}/rename"),
    ("POST", "/players/{playerId}/change-origin"),
    ("POST", "/players/{playerId}/heal"),
    ("POST", "/players/{playerId}/sell"),
    ("GET", "/players/{playerId}/anti-age-upgrade-options"),
    ("POST", "/players/{playerId}/anti-age-upgrade"),
    ("GET", "/lineup/current"),
    ("PUT", "/lineup/current"),
    ("GET", "/lineup/upcoming"),
    ("PUT", "/lineup/upcoming/{fixtureId}"),
    ("GET", "/tactics"),
    ("PUT", "/tactics"),
    ("GET", "/lineup/lock-status/{fixtureId}"),
    ("POST", "/lineup/queue-change/{fixtureId}"),
    ("GET", "/training/overview"),
    ("POST", "/training/team"),
    ("POST", "/training/individual"),
    ("POST", "/training/camps/{campId}/book"),
    ("POST", "/training/tactics/{tacticId}/train"),
    ("GET", "/training/progress"),
    ("GET", "/training/formulas"),
    ("GET", "/training/individual-tiers"),
    ("GET", "/training/camps/{campId}/repeat-cost"),
    ("GET", "/scouting/overview"),
    ("POST", "/scouting/instruct"),
    ("POST", "/scouting/instruct-special"),
    ("POST", "/scouting/speedup"),
    ("GET", "/scouting/results"),
    ("POST", "/scouting/results/{resultId}/sign"),
    ("GET", "/scouting/probability-state"),
    ("GET", "/transfer/auctions"),
    ("GET", "/transfer/auctions/{auctionId}"),
    ("POST", "/transfer/auctions/{auctionId}/bid"),
    ("POST", "/transfer/auctions/{auctionId}/favorite"),
    ("DELETE", "/transfer/auctions/{auctionId}/favorite"),
    ("GET", "/transfer/my-sales"),
    ("GET", "/transfer/my-bids"),
    ("GET", "/transfer/favorites"),
    ("GET", "/transfer/seasonal-injections"),
    ("GET", "/league/current"),
    ("GET", "/league/table"),
    ("GET", "/league/fixtures"),
    ("GET", "/league/results"),
    ("GET", "/league/topscorers"),
    ("GET", "/matches/{matchId}"),
    ("GET", "/matches/{matchId}/live"),
    ("GET", "/matches/{matchId}/report"),
    ("POST", "/matches/{matchId}/live/substitute"),
    ("POST", "/matches/{matchId}/live/change-formation"),
    ("GET", "/ucl/current"),
    ("GET", "/ucl/fixtures"),
    ("GET", "/ucl/table"),
    ("GET", "/cups/current"),
    ("GET", "/cups/fixtures"),
    ("GET", "/cups/bracket"),
    ("GET", "/ladder/overview"),
    ("GET", "/ladder/fixtures"),
    ("POST", "/ladder/matches/{matchId}/start"),
    ("POST", "/ladder/stamina/refill"),
    ("GET", "/ladder/ranking"),
    ("GET", "/friends"),
    ("POST", "/friends/search"),
    ("POST", "/friends/requests/{managerId}"),
    ("POST", "/friends/requests/{requestId}/accept"),
    ("POST", "/friends/requests/{requestId}/decline"),
    ("DELETE", "/friends/{friendId}"),
    ("POST", "/friendlies/invite"),
    ("GET", "/friendlies/requests"),
    ("GET", "/friends/series"),
    ("PUT", "/friends/series"),
    ("GET", "/clubs/{clubId}/public-squad"),
    ("GET", "/chat/channels"),
    ("GET", "/chat/channels/{channelId}/messages"),
    ("POST", "/chat/channels/{channelId}/messages"),
    ("POST", "/chat/groups"),
    ("GET", "/chat/private/{managerId}"),
    ("GET", "/shop/catalog"),
    ("POST", "/shop/offers/{offerId}/grant"),
    ("GET", "/shop/grants/history"),
    ("GET", "/shop/events"),
    ("GET", "/shop/premium/tiers"),
    ("POST", "/shop/premium/{tierId}/grant"),
    ("GET", "/equipment/catalog"),
    ("POST", "/equipment/shirts/{id}/buy"),
    ("POST", "/equipment/emblems/{id}/buy"),
    ("POST", "/equipment/perks/{id}/activate"),
    ("GET", "/equipment/perks/pricing"),
    ("POST", "/alliances"),
    ("GET", "/alliances/{allianceId}"),
    ("POST", "/alliances/{allianceId}/join-request"),
    ("POST", "/alliances/{allianceId}/members/{memberId}/approve"),
    ("POST", "/alliances/{allianceId}/members/{memberId}/kick"),
    ("GET", "/alliances/{allianceId}/chat"),
    ("GET", "/alliances/{allianceId}/board"),
    ("POST", "/alliances/{allianceId}/board/threads"),
    ("GET", "/alliances/{allianceId}/cup"),
    ("POST", "/alliances/{allianceId}/cup/lineup"),
    ("GET", "/tasks/onboarding"),
    ("GET", "/tasks/daily"),
    ("GET", "/tasks/weekly"),
    ("POST", "/tasks/{taskId}/claim"),
    ("POST", "/admin/ticks/run"),
    ("POST", "/admin/bots/run-cycle"),
    ("POST", "/admin/seasons/rollover"),
    ("GET", "/admin/health/deep"),
    ("POST", "/admin/precompute/run"),
    ("POST", "/admin/training-tick/run"),
    ("POST", "/admin/training-tick/catchup"),
    ("POST", "/admin/transfer/injections/run"),
]


def _contract_response(request: Request) -> dict:
    return ok(
        {
            "endpoint": request.url.path,
            "method": request.method,
            "params": dict(request.path_params),
            "query": dict(request.query_params),
            "status": "implemented-placeholder",
        }
    )


def _register_contract_endpoint(method: str, path: str) -> None:
    async def _handler(request: Request) -> dict:
        return _contract_response(request)

    router.add_api_route(path, _handler, methods=[method], include_in_schema=True)


for _method, _path in CONTRACT_ENDPOINTS:
    if _path in {
        "/auth/login",
        "/bootstrap",
        "/club",
        "/runtime/calendar",
        "/runtime/locks",
        "/admin/ticks/run",
        "/admin/bots/run-cycle",
        "/admin/seasons/rollover",
        "/admin/health/deep",
        "/admin/precompute/run",
        "/admin/training-tick/run",
        "/admin/training-tick/catchup",
        "/admin/transfer/injections/run",
    }:
        continue
    _register_contract_endpoint(_method, _path)


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


@router.get("/runtime/calendar")
def runtime_calendar() -> dict:
    return ok(RUNTIME_STATE.runtime_calendar())


@router.get("/runtime/locks")
def runtime_locks() -> dict:
    return ok(RUNTIME_STATE.runtime_locks())


@router.post("/admin/precompute/run")
def admin_precompute_run(competition: str = "league") -> dict:
    result = RUNTIME_STATE.run_precompute(competition)
    return ok(result)


@router.post("/admin/ticks/run")
def admin_ticks_run() -> dict:
    return ok(RUNTIME_STATE.run_ticks())


@router.post("/admin/bots/run-cycle")
def admin_bots_cycle() -> dict:
    return ok(RUNTIME_STATE.run_bot_cycle())


@router.post("/admin/seasons/rollover")
def admin_rollover() -> dict:
    return ok(RUNTIME_STATE.rollover())


@router.get("/admin/health/deep")
def admin_health_deep() -> dict:
    return ok(RUNTIME_STATE.deep_health())


@router.post("/admin/training-tick/run")
def admin_training_tick_run() -> dict:
    return ok(RUNTIME_STATE.run_training_tick())


@router.post("/admin/training-tick/catchup")
def admin_training_tick_catchup(days: int = 1) -> dict:
    results = [RUNTIME_STATE.run_training_tick() for _ in range(max(1, min(days, 30)))]
    return ok({"days": days, "runs": results})


@router.post("/admin/transfer/injections/run")
def admin_transfer_injections_run() -> dict:
    return ok(RUNTIME_STATE.run_transfer_injections())


@router.websocket("/realtime")
async def realtime(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(
        {
            "ok": True,
            "data": {
                "event": "realtime.connected",
                "topics": [
                    "chat",
                    "live-match-events",
                    "notifications",
                    "market-updates",
                ],
            },
        }
    )
    await websocket.close()
