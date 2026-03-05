from random import Random
import pytest

from app.domain.bots import BotProfile, alliance_overbid_chance, daily_star_budget, draw_persona


def test_persona_draw_is_stable_with_seed() -> None:
    rng = Random(42)
    assert draw_persona(rng) in {"transfer", "training", "balanced", "ladder", "youth"}


def test_daily_star_budget_non_negative() -> None:
    rng = Random(1)
    profile = BotProfile(persona="balanced", activeness=60, star_buyer=55, alliance_loyalty=50)
    assert daily_star_budget(profile, league_bonus=250, rng=rng) >= 0


def test_alliance_overbid_has_floor() -> None:
    profile = BotProfile(persona="youth", activeness=30, star_buyer=10, alliance_loyalty=100)
    assert alliance_overbid_chance(profile) == pytest.approx(0.05)
