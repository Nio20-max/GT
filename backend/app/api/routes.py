from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from fastapi import APIRouter, Header, Request, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.api.envelope import error, ok
from app.core.config import settings
from app.domain.training import TrainingContext, daily_gain
from app.services.auth_store import AUTH_STORE
from app.services.game_store import GAME_STORE
from app.services.persistent_json import JsonStateFile
from app.services.runtime_state import RUNTIME_STATE

router = APIRouter(prefix="/api/v1")


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        sanitized = value.strip().lower()
        if not sanitized.replace("_", "").replace("-", "").isalnum():
            raise ValueError("username must be alphanumeric, dash, or underscore")
        return sanitized


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: str = Field(min_length=5, max_length=128)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        sanitized = value.strip().lower()
        if not sanitized.replace("_", "").replace("-", "").isalnum():
            raise ValueError("username must be alphanumeric, dash, or underscore")
        return sanitized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        sanitized = value.strip().lower()
        if "@" not in sanitized or sanitized.startswith("@") or sanitized.endswith("@"):
            raise ValueError("email must be valid")
        return sanitized


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
    path = request.scope.get("route").path if request.scope.get("route") else request.url.path
    return CONTRACT_STATE.handle(
        method=request.method,
        path=path,
        params=dict(request.path_params),
        query=dict(request.query_params),
    )


class ContractState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._state_file = JsonStateFile(settings.state_dir_path / "contract_state.json")
        loaded = self._state_file.load(default={"state": {}})
        if isinstance(loaded, dict) and isinstance(loaded.get("state"), dict):
            self._state = loaded["state"]
        else:
            self._state = {}

    def _save(self) -> None:
        self._state_file.save({"state": self._state})

    def _default_payload(self, path: str, params: dict, query: dict) -> dict:
        if path.startswith("/league"):
            return {"season": RUNTIME_STATE.season_id, "fixtures": len(RUNTIME_STATE.fixtures)}
        if path.startswith("/training"):
            return RUNTIME_STATE.run_training_tick(sample_players=16)
        if path.startswith("/transfer"):
            return {"auctions": [], "favorites": [], "query": query}
        if path.startswith("/scouting"):
            return {"results": [], "probability": {"base": 0.12}}
        if path.startswith("/friends"):
            return {"friends": [], "requests": []}
        if path.startswith("/chat"):
            return {"messages": [], "channels": []}
        if path.startswith("/shop") or path.startswith("/equipment"):
            return {"catalog": [], "currency": {"money": 5000000, "stars": 20000}}
        if path.startswith("/alliances"):
            return {"alliances": [], "params": params}
        if path.startswith("/tasks"):
            return {"tasks": [], "claimed": False}
        if path.startswith("/stadium"):
            return {"level": 1, "buildings": [], "pricing": {"standard": 15}}
        if path.startswith("/players") or path.startswith("/squad"):
            return {"players": [], "playerId": params.get("playerId")}
        if path.startswith("/matches"):
            return {"matchId": params.get("matchId"), "status": "scheduled"}
        if path.startswith("/ucl") or path.startswith("/cups"):
            return {"season": RUNTIME_STATE.season_id, "fixtures": []}
        if path.startswith("/club"):
            return {"clubId": params.get("clubId", "self"), "name": "GT Dev Club"}
        if path.startswith("/finances"):
            return {"money": 5000000, "stars": 20000, "entries": []}
        if path.startswith("/runtime"):
            return RUNTIME_STATE.runtime_locks()
        return {"params": params, "query": query}

    def handle(self, method: str, path: str, params: dict, query: dict, body: dict | None = None) -> dict:
        key = f"{path}:{sorted(params.items())}:{sorted(query.items())}"
        with self._lock:
            existing = self._state.get(key)
            if method == "GET":
                data = existing if existing is not None else self._default_payload(path, params, query)
            elif method in {"POST", "PUT", "PATCH"}:
                merged = {}
                if isinstance(existing, dict):
                    merged.update(existing)
                if isinstance(body, dict):
                    merged.update(body)
                if not merged:
                    merged = self._default_payload(path, params, query)
                merged["updatedAtUtc"] = datetime.now(timezone.utc).isoformat()
                self._state[key] = merged
                self._save()
                data = merged
            elif method == "DELETE":
                deleted = key in self._state
                self._state.pop(key, None)
                self._save()
                data = {"deleted": deleted}
            else:
                data = self._default_payload(path, params, query)

        return ok(
            {
                "endpoint": path,
                "method": method,
                "params": params,
                "query": query,
                "data": data,
            }
        )


CONTRACT_STATE = ContractState()


def _api_error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=error(code, message))


def _register_contract_endpoint(method: str, path: str) -> None:
    async def _handler(request: Request) -> dict:
        body: dict | None = None
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                candidate = await request.json()
                body = candidate if isinstance(candidate, dict) else None
            except Exception:
                body = None
        path_template = request.scope.get("route").path if request.scope.get("route") else request.url.path
        return CONTRACT_STATE.handle(
            method=request.method,
            path=path_template,
            params=dict(request.path_params),
            query=dict(request.query_params),
            body=body,
        )

    router.add_api_route(path, _handler, methods=[method], include_in_schema=True)


for _method, _path in CONTRACT_ENDPOINTS:
    if _path in {
        "/auth/register",
        "/auth/login",
        "/bootstrap",
        "/club",
        "/squad",
        "/league/current",
        "/league/table",
        "/league/results",
        "/me/profile",
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
    try:
        user, token = AUTH_STORE.login(payload.username, payload.password)
    except ValueError:
        return _api_error(401, "AUTH_INVALID_CREDENTIALS", "Invalid username or password")
    return ok(
        {
            "token": token,
            "refreshToken": f"refresh-{token}",
            "expiresIn": 3600,
            "user": {"id": user.user_id, "username": user.username, "email": user.email},
        }
    )


@router.post("/auth/register")
def register(payload: RegisterRequest) -> dict:
    try:
        user = AUTH_STORE.register(username=payload.username, email=payload.email, password=payload.password)
    except ValueError:
        return _api_error(409, "AUTH_USERNAME_EXISTS", "Username already exists")
    GAME_STORE.ensure_user_game_state(user)
    return JSONResponse(
        status_code=201,
        content=ok({"created": True, "user": {"id": user.user_id, "username": user.username, "email": user.email}}),
    )


@router.get("/me/profile")
def me_profile(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        return ok({"authenticated": False, "user": None})
    token = authorization.split(" ", 1)[1].strip()
    user = AUTH_STORE.from_token(token)
    if user is None:
        return ok({"authenticated": False, "user": None})
    GAME_STORE.ensure_user_game_state(user)
    return ok({"authenticated": True, "user": {"id": user.user_id, "username": user.username, "email": user.email}})


def _require_user(authorization: str | None) -> tuple[dict | None, JSONResponse | None]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None, _api_error(401, "AUTH_REQUIRED", "Bearer token required")

    token = authorization.split(" ", 1)[1].strip()
    user = AUTH_STORE.from_token(token)
    if user is None:
        return None, _api_error(401, "AUTH_INVALID_TOKEN", "Session expired or invalid")
    return {"id": user.user_id, "username": user.username, "email": user.email}, None


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
def club(authorization: str | None = Header(default=None)) -> dict:
    user, auth_error = _require_user(authorization)
    if auth_error is not None:
        return auth_error

    club_record = GAME_STORE.club_for_user(user_id=user["id"])
    if club_record is None:
        auth_user = AUTH_STORE.from_user_id(user["id"])
        if auth_user is None:
            return _api_error(404, "CLUB_NOT_FOUND", "Club not found")
        club_record = GAME_STORE.ensure_user_game_state(auth_user)

    return ok(
        {
            "clubId": club_record.club_id,
            "name": club_record.name,
            "money": club_record.money,
            "stars": club_record.stars,
            "leagueId": club_record.league_id,
            "strength": 100,
        }
    )


@router.get("/squad")
def squad(authorization: str | None = Header(default=None)) -> dict:
    user, auth_error = _require_user(authorization)
    if auth_error is not None:
        return auth_error

    players = GAME_STORE.squad_for_user(user_id=user["id"])
    return ok(
        {
            "count": len(players),
            "players": [player.__dict__ for player in players],
        }
    )


@router.get("/league/current")
def league_current() -> dict:
    return ok(
        {
            "seasonId": RUNTIME_STATE.season_id,
            "leagueSize": 12,
            "scheduledFixtures": len([f for f in RUNTIME_STATE.fixtures if f.competition == "league"]),
        }
    )


@router.get("/league/table")
def league_table() -> dict:
    table: dict[int, dict] = {}
    for fixture in RUNTIME_STATE.fixtures:
        if fixture.competition != "league" or fixture.status != "published":
            continue
        if fixture.result_home is None or fixture.result_away is None:
            continue

        home = table.setdefault(
            fixture.home_team,
            {"clubId": fixture.home_team, "played": 0, "wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0, "points": 0},
        )
        away = table.setdefault(
            fixture.away_team,
            {"clubId": fixture.away_team, "played": 0, "wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0, "points": 0},
        )

        home["played"] += 1
        away["played"] += 1
        home["gf"] += fixture.result_home
        home["ga"] += fixture.result_away
        away["gf"] += fixture.result_away
        away["ga"] += fixture.result_home

        if fixture.result_home > fixture.result_away:
            home["wins"] += 1
            home["points"] += 3
            away["losses"] += 1
        elif fixture.result_home < fixture.result_away:
            away["wins"] += 1
            away["points"] += 3
            home["losses"] += 1
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    rows = sorted(table.values(), key=lambda row: (row["points"], row["gf"] - row["ga"], row["gf"]), reverse=True)
    return ok({"seasonId": RUNTIME_STATE.season_id, "rows": rows})


@router.get("/league/results")
def league_results() -> dict:
    published = [
        {
            "fixtureId": fixture.fixture_id,
            "homeClubId": fixture.home_team,
            "awayClubId": fixture.away_team,
            "homeGoals": fixture.result_home,
            "awayGoals": fixture.result_away,
            "status": fixture.status,
        }
        for fixture in RUNTIME_STATE.fixtures
        if fixture.competition == "league" and fixture.status == "published"
    ]
    return ok({"seasonId": RUNTIME_STATE.season_id, "results": published})


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
