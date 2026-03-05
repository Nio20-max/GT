from app.domain.training import TrainingContext, daily_gain, fatigue_factor, high_strength_factor


def test_high_strength_factor_drops_after_700() -> None:
    assert high_strength_factor(650) == 1.0
    assert high_strength_factor(900) < 1.0


def test_fatigue_factor_is_bounded() -> None:
    assert fatigue_factor(-10) == 1.0
    assert fatigue_factor(100) == 0.55


def test_daily_gain_not_too_high_for_balanced_midfielder() -> None:
    ctx = TrainingContext(
        age=25,
        strength=500,
        talent=6,
        style="balanced",
        skill_bucket="midfield",
        fatigue=20,
    )
    gain = daily_gain(ctx)
    assert 0.8 <= gain <= 1.6


def test_age_decay_can_zero_growth_for_older_player() -> None:
    ctx = TrainingContext(
        age=34,
        strength=850,
        talent=4,
        style="conservative",
        skill_bucket="defense",
        fatigue=85,
    )
    assert daily_gain(ctx) >= 0.0
