"""Deterministic match engine – no I/O, pure computation."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field

from app.core.config import settings


# ── Data classes ─────────────────────────────────────────────────────────
@dataclass
class TeamStats:
    """Aggregated team stats fed into the engine."""

    attack: float = 0.0   # sum of attacker skill values
    midfield: float = 0.0
    defense: float = 0.0
    goalkeeping: float = 0.0
    tactic_attack: float = 0.0
    tactic_defense: float = 0.0
    perk_attack: float = 0.0
    perk_defense: float = 0.0
    morale: float = 50.0
    fitness: float = 100.0
    finishing: float = 50.0
    set_pieces: float = 50.0


@dataclass
class MatchInput:
    match_id: str
    competition: str      # league / cup / ucl
    season_id: str
    home: TeamStats
    away: TeamStats
    is_knockout: bool = False
    base_chances: float = 10.0
    base_xg: float = 0.12
    min_chances: int = 4
    max_chances: int = 22


@dataclass
class MatchEventRecord:
    minute: int
    event_type: str   # goal, save, miss
    team: str         # home / away
    detail: str = ""


@dataclass
class MatchOutput:
    home_goals: int = 0
    away_goals: int = 0
    home_penalty_goals: int | None = None
    away_penalty_goals: int | None = None
    events: list[MatchEventRecord] = field(default_factory=list)
    seed_hex: str = ""


# ── Helpers ──────────────────────────────────────────────────────────────
def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _make_seed(inp: MatchInput, server_secret: str | None = None) -> str:
    secret = server_secret or settings.server_secret
    raw = f"{inp.match_id}{inp.competition}{inp.season_id}{settings.seed_version}{secret}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _attack_index(ts: TeamStats) -> float:
    return (
        0.45 * ts.attack
        + 0.30 * ts.midfield
        + 0.10 * ts.tactic_attack
        + 0.10 * ts.perk_attack
        + 0.05 * ts.morale
    )


def _defense_index(ts: TeamStats) -> float:
    return (
        0.45 * ts.defense
        + 0.25 * ts.goalkeeping
        + 0.15 * ts.tactic_defense
        + 0.10 * ts.perk_defense
        + 0.05 * ts.fitness
    )


def _tempo_modifier(competition: str) -> float:
    return {"league": 1.0, "cup": 1.05, "ucl": 1.10}.get(competition, 1.0)


# ── Core simulation ─────────────────────────────────────────────────────
def simulate_match(
    inp: MatchInput,
    server_secret: str | None = None,
) -> MatchOutput:
    """Run a fully deterministic match simulation."""
    seed_hex = _make_seed(inp, server_secret)
    rng = random.Random(seed_hex)

    tempo_mod = _tempo_modifier(inp.competition)

    # Home attack vs away defence
    home_atk = _attack_index(inp.home)
    away_def = _defense_index(inp.away)
    away_atk = _attack_index(inp.away)
    home_def = _defense_index(inp.home)

    # Avoid division by zero
    away_def = max(away_def, 1.0)
    home_def = max(home_def, 1.0)

    home_chances = int(
        _clamp(
            round(inp.base_chances * (home_atk / away_def) * tempo_mod),
            inp.min_chances,
            inp.max_chances,
        )
    )
    away_chances = int(
        _clamp(
            round(inp.base_chances * (away_atk / home_def) * tempo_mod),
            inp.min_chances,
            inp.max_chances,
        )
    )

    events: list[MatchEventRecord] = []
    home_goals = 0
    away_goals = 0

    def _resolve_chances(
        n_chances: int,
        team_label: str,
        finishing: float,
        opp_gk: float,
        sp: float,
    ) -> int:
        nonlocal events
        goals = 0
        finishing_mod = 1.0 + (finishing - 50) / 200
        keeper_opp_mod = 1.0 - (opp_gk - 50) / 200
        setpiece_mod = 1.0 + (sp - 50) / 400
        p_goal = _clamp(
            inp.base_xg * finishing_mod * keeper_opp_mod * setpiece_mod, 0.02, 0.65
        )
        for _ in range(n_chances):
            minute = rng.randint(1, 90)
            if rng.random() < p_goal:
                goals += 1
                events.append(
                    MatchEventRecord(minute=minute, event_type="goal", team=team_label)
                )
            else:
                evt = rng.choice(["save", "miss"])
                events.append(
                    MatchEventRecord(minute=minute, event_type=evt, team=team_label)
                )
        return goals

    home_goals = _resolve_chances(
        home_chances, "home", inp.home.finishing, inp.away.goalkeeping, inp.home.set_pieces
    )
    away_goals = _resolve_chances(
        away_chances, "away", inp.away.finishing, inp.home.goalkeeping, inp.away.set_pieces
    )

    events.sort(key=lambda e: e.minute)

    output = MatchOutput(
        home_goals=home_goals,
        away_goals=away_goals,
        events=events,
        seed_hex=seed_hex,
    )

    # Knockout: penalty shootout on draw
    if inp.is_knockout and home_goals == away_goals:
        h_pen, a_pen = _penalty_shootout(rng)
        output.home_penalty_goals = h_pen
        output.away_penalty_goals = a_pen

    return output


def _penalty_shootout(rng: random.Random) -> tuple[int, int]:
    """Simulate a best-of-5 (then sudden-death) penalty shootout."""
    home_scored = 0
    away_scored = 0
    for i in range(5):
        if rng.random() < 0.75:
            home_scored += 1
        if rng.random() < 0.75:
            away_scored += 1
    if home_scored != away_scored:
        return home_scored, away_scored
    # Sudden death
    for _ in range(20):
        h = rng.random() < 0.75
        a = rng.random() < 0.75
        if h:
            home_scored += 1
        if a:
            away_scored += 1
        if h != a:
            break
    return home_scored, away_scored
