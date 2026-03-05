"""Tests for match engine determinism."""

from app.services.match_engine import MatchInput, TeamStats, simulate_match


def _make_input(**overrides) -> MatchInput:
    defaults = dict(
        match_id="fixture-001",
        competition="league",
        season_id="s1",
        home=TeamStats(
            attack=500, midfield=400, defense=450, goalkeeping=300,
            tactic_attack=50, tactic_defense=50, perk_attack=20, perk_defense=20,
            morale=60, fitness=90, finishing=55, set_pieces=50,
        ),
        away=TeamStats(
            attack=480, midfield=420, defense=440, goalkeeping=310,
            tactic_attack=45, tactic_defense=55, perk_attack=15, perk_defense=25,
            morale=55, fitness=85, finishing=50, set_pieces=45,
        ),
    )
    defaults.update(overrides)
    return MatchInput(**defaults)


def test_same_seed_same_result():
    """Running the engine twice with identical inputs must yield identical output."""
    inp = _make_input()
    secret = "test-secret"
    r1 = simulate_match(inp, server_secret=secret)
    r2 = simulate_match(inp, server_secret=secret)
    assert r1.home_goals == r2.home_goals
    assert r1.away_goals == r2.away_goals
    assert r1.seed_hex == r2.seed_hex
    assert len(r1.events) == len(r2.events)
    for e1, e2 in zip(r1.events, r2.events):
        assert e1.minute == e2.minute
        assert e1.event_type == e2.event_type
        assert e1.team == e2.team


def test_different_match_id_different_result():
    """Different match_id should (very likely) produce different output."""
    secret = "test-secret"
    r1 = simulate_match(_make_input(match_id="a"), server_secret=secret)
    r2 = simulate_match(_make_input(match_id="b"), server_secret=secret)
    assert r1.seed_hex != r2.seed_hex


def test_knockout_penalty_on_draw():
    """Knockout match with equal teams should eventually decide via penalties."""
    inp = _make_input(
        is_knockout=True,
        home=TeamStats(
            attack=400, midfield=400, defense=400, goalkeeping=400,
            tactic_attack=50, tactic_defense=50, perk_attack=10, perk_defense=10,
            morale=50, fitness=100, finishing=50, set_pieces=50,
        ),
        away=TeamStats(
            attack=400, midfield=400, defense=400, goalkeeping=400,
            tactic_attack=50, tactic_defense=50, perk_attack=10, perk_defense=10,
            morale=50, fitness=100, finishing=50, set_pieces=50,
        ),
    )
    # Run many times – at least some should go to penalties
    went_to_pens = False
    for i in range(50):
        result = simulate_match(
            MatchInput(
                match_id=f"ko-{i}",
                competition="cup",
                season_id="s1",
                home=inp.home,
                away=inp.away,
                is_knockout=True,
            ),
            server_secret="pen-test",
        )
        if result.home_penalty_goals is not None:
            went_to_pens = True
            assert result.home_penalty_goals != result.away_penalty_goals
            break
    assert went_to_pens, "Expected at least one draw → penalty shootout in 50 tries"


def test_events_sorted_by_minute():
    result = simulate_match(_make_input(), server_secret="sort-test")
    minutes = [e.minute for e in result.events]
    assert minutes == sorted(minutes)


def test_goals_in_valid_range():
    result = simulate_match(_make_input(), server_secret="range-test")
    assert result.home_goals >= 0
    assert result.away_goals >= 0
