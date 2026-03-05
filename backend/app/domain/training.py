from __future__ import annotations

from dataclasses import dataclass
from math import exp

STYLE_MULTIPLIER = {
    "conservative": 0.88,
    "balanced": 1.00,
    "aggressive": 1.14,
}

AGE_MULTIPLIER = {
    21: 1.16,
    24: 1.06,
    27: 1.00,
    29: 0.90,
    30: 0.75,
    31: 0.68,
    32: 0.60,
    33: 0.50,
    34: 0.38,
}

# Discovered baseline constants from empirical sanity tests (user requested conservative gains).
BASE_GAIN_BY_SKILL = {
    "goalkeeper": 1.30,
    "defense": 1.22,
    "midfield": 1.18,
    "attack": 1.15,
}


@dataclass(frozen=True)
class TrainingContext:
    age: int
    strength: float
    talent: int  # 1..10
    style: str  # conservative|balanced|aggressive
    skill_bucket: str  # goalkeeper|defense|midfield|attack
    camp_multiplier: float = 1.0
    individual_multiplier: float = 1.0
    tactic_multiplier: float = 1.0
    fatigue: float = 0.0  # 0..100


def talent_factor(talent: int) -> float:
    return 0.85 + 0.03 * max(1, min(10, talent))


def age_factor(age: int) -> float:
    if age <= 21:
        return AGE_MULTIPLIER[21]
    if age <= 24:
        return AGE_MULTIPLIER[24]
    if age <= 27:
        return AGE_MULTIPLIER[27]
    if age <= 29:
        return AGE_MULTIPLIER[29]
    return AGE_MULTIPLIER.get(age, 0.38)


def high_strength_factor(strength: float) -> float:
    if strength <= 700:
        return 1.0
    return exp(-((strength - 700) / 220.0))


def fatigue_factor(fatigue: float) -> float:
    bounded = max(0.0, min(100.0, fatigue))
    # Conservative linear model validated in discovery: max penalty 45% at fatigue=100.
    return max(0.55, 1.0 - 0.0045 * bounded)


def age_decay(age: int) -> float:
    if age < 30:
        return 0.0
    return 0.05 * (age - 29)


def daily_gain(ctx: TrainingContext) -> float:
    base = BASE_GAIN_BY_SKILL[ctx.skill_bucket]
    gain = (
        base
        * STYLE_MULTIPLIER[ctx.style]
        * talent_factor(ctx.talent)
        * age_factor(ctx.age)
        * high_strength_factor(ctx.strength)
        * ctx.camp_multiplier
        * ctx.individual_multiplier
        * ctx.tactic_multiplier
        * fatigue_factor(ctx.fatigue)
    )
    return max(0.0, gain - age_decay(ctx.age))
