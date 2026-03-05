from __future__ import annotations

from dataclasses import dataclass
from random import Random

PERSONA_DISTRIBUTION = (
    ("transfer", 25),
    ("training", 20),
    ("balanced", 25),
    ("ladder", 15),
    ("youth", 15),
)


@dataclass(frozen=True)
class BotProfile:
    persona: str
    activeness: int
    star_buyer: int
    alliance_loyalty: int


def draw_persona(rng: Random) -> str:
    n = rng.randint(1, 100)
    c = 0
    for persona, weight in PERSONA_DISTRIBUTION:
        c += weight
        if n <= c:
            return persona
    return "balanced"


def daily_star_budget(profile: BotProfile, league_bonus: int, rng: Random) -> int:
    base = rng.randint(200, 1800)
    value = base + profile.activeness * 8 + profile.star_buyer * 12 + league_bonus
    jitter = int(value * (rng.uniform(-0.10, 0.10)))
    return max(0, value + jitter)


def alliance_overbid_chance(profile: BotProfile) -> float:
    return max(0.05, 0.40 - 0.35 * (profile.alliance_loyalty / 100.0))
