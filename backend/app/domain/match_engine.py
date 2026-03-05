from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import random


@dataclass(frozen=True)
class TeamVector:
    attack: float
    midfield: float
    defense: float


@dataclass(frozen=True)
class MatchInput:
    match_id: int
    competition: str
    season_id: int
    seed_version: int
    server_secret: str
    home: TeamVector
    away: TeamVector


def compute_seed(match: MatchInput) -> int:
    raw = (
        f"{match.match_id}|{match.competition}|{match.season_id}|"
        f"{match.seed_version}|{match.server_secret}"
    )
    return int(sha256(raw.encode("utf-8")).hexdigest()[:16], 16)


def simulate_result(match: MatchInput) -> dict[str, int]:
    rng = random.Random(compute_seed(match))

    home_quality = 0.45 * match.home.attack + 0.30 * match.home.midfield + 0.25 * match.home.defense
    away_quality = 0.45 * match.away.attack + 0.30 * match.away.midfield + 0.25 * match.away.defense

    quality_delta = (home_quality - away_quality) / 80.0
    base_home = 1.2 + max(-0.6, min(0.9, quality_delta))
    base_away = 1.0 + max(-0.6, min(0.9, -quality_delta))

    # Poisson-like counting with bounded minute-level chance buckets.
    home_goals = 0
    away_goals = 0
    for _ in range(12):
        if rng.random() < (base_home / 12.0):
            home_goals += 1
        if rng.random() < (base_away / 12.0):
            away_goals += 1

    return {"homeGoals": home_goals, "awayGoals": away_goals}
