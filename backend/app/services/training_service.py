"""Training tick calculation – fully deterministic, no I/O."""

from __future__ import annotations

import math
from dataclasses import dataclass

# ── Style multipliers ────────────────────────────────────────────────────
STYLE_MULTIPLIERS: dict[str, float] = {
    "conservative": 0.88,
    "balanced": 1.00,
    "aggressive": 1.14,
}

# ── Age multipliers ──────────────────────────────────────────────────────
AGE_MULTIPLIERS: dict[int, float] = {
    21: 1.16,  # <=21 uses this
    22: 1.06,
    23: 1.06,
    24: 1.06,
    25: 1.00,
    26: 1.00,
    27: 1.00,
    28: 0.90,
    29: 0.90,
    30: 0.75,
    31: 0.68,
    32: 0.60,
    33: 0.50,
    34: 0.38,
}


def _age_mult(age: int) -> float:
    if age <= 21:
        return 1.16
    if age >= 34:
        return 0.38
    return AGE_MULTIPLIERS.get(age, 1.00)


def talent_factor(talent: int) -> float:
    """talent_factor = 0.85 + 0.03 * talent  (talent 1-10)."""
    return 0.85 + 0.03 * talent


def high_strength_factor(strength: float) -> float:
    """Diminishing returns above S=700."""
    if strength <= 700:
        return 1.0
    return math.exp(-(strength - 700) / 220)


@dataclass
class TrainingInput:
    """All inputs needed to compute one player's daily training gain."""

    current_strength: float
    age: int
    talent: int  # 1-10
    style: str  # conservative / balanced / aggressive
    base_gain: float = 2.0
    camp_mult: float = 1.0
    indiv_mult: float = 1.0
    tactic_mult: float = 1.0
    fatigue_mult: float = 1.0
    has_anti_age: bool = False


@dataclass
class TrainingResult:
    gain: float
    decay: float
    new_strength: float


def compute_training_tick(inp: TrainingInput) -> TrainingResult:
    """Pure function: compute one player's daily training result."""
    style_mult = STYLE_MULTIPLIERS.get(inp.style, 1.0)
    tf = talent_factor(inp.talent)
    am = _age_mult(inp.age)
    hsf = high_strength_factor(inp.current_strength)

    gain = (
        inp.base_gain
        * style_mult
        * tf
        * am
        * hsf
        * inp.camp_mult
        * inp.indiv_mult
        * inp.tactic_mult
        * inp.fatigue_mult
    )

    # Decay for old players
    decay = 0.0
    if inp.age >= 30 and not inp.has_anti_age:
        decay = 0.05 * (inp.age - 29)

    new_strength = min(1000.0, inp.current_strength + gain - decay)
    return TrainingResult(gain=gain, decay=decay, new_strength=new_strength)
