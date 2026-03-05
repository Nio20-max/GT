"""Tests for training gain calculation."""

from app.services.training_service import TrainingInput, compute_training_tick, talent_factor, high_strength_factor


def test_talent_factor():
    assert talent_factor(1) == 0.88
    assert talent_factor(5) == 1.0
    assert talent_factor(10) == 1.15


def test_high_strength_factor_below_700():
    assert high_strength_factor(500) == 1.0
    assert high_strength_factor(700) == 1.0


def test_high_strength_factor_above_700():
    result = high_strength_factor(800)
    assert 0.0 < result < 1.0


def test_balanced_young_player():
    inp = TrainingInput(
        current_strength=400.0,
        age=20,
        talent=5,
        style="balanced",
    )
    result = compute_training_tick(inp)
    # Young balanced talent-5 player: gain = 2.0 * 1.0 * 1.0 * 1.16 * 1.0 * 1 * 1 * 1 * 1
    expected_gain = 2.0 * 1.0 * 1.0 * 1.16 * 1.0
    assert abs(result.gain - expected_gain) < 1e-9
    assert result.decay == 0.0
    assert result.new_strength == 400.0 + expected_gain


def test_aggressive_style_boost():
    inp = TrainingInput(current_strength=400.0, age=25, talent=5, style="aggressive")
    result = compute_training_tick(inp)
    inp_b = TrainingInput(current_strength=400.0, age=25, talent=5, style="balanced")
    result_b = compute_training_tick(inp_b)
    assert result.gain > result_b.gain


def test_decay_at_age_30_no_anti_age():
    inp = TrainingInput(current_strength=600.0, age=30, talent=5, style="balanced")
    result = compute_training_tick(inp)
    assert result.decay == 0.05 * (30 - 29)
    assert result.new_strength == 600.0 + result.gain - result.decay


def test_no_decay_at_age_30_with_anti_age():
    inp = TrainingInput(
        current_strength=600.0, age=30, talent=5, style="balanced", has_anti_age=True
    )
    result = compute_training_tick(inp)
    assert result.decay == 0.0


def test_strength_capped_at_1000():
    inp = TrainingInput(current_strength=999.5, age=18, talent=10, style="aggressive")
    result = compute_training_tick(inp)
    assert result.new_strength == 1000.0


def test_decay_increases_with_age():
    r30 = compute_training_tick(TrainingInput(current_strength=600, age=30, talent=5, style="balanced"))
    r34 = compute_training_tick(TrainingInput(current_strength=600, age=34, talent=5, style="balanced"))
    assert r34.decay > r30.decay
