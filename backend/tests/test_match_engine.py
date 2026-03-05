from app.domain.match_engine import MatchInput, TeamVector, compute_seed, simulate_result


def _sample_match() -> MatchInput:
    return MatchInput(
        match_id=101,
        competition="league",
        season_id=1,
        seed_version=1,
        server_secret="secret",
        home=TeamVector(78, 75, 73),
        away=TeamVector(73, 72, 71),
    )


def test_seed_is_deterministic() -> None:
    match = _sample_match()
    assert compute_seed(match) == compute_seed(match)


def test_result_is_deterministic() -> None:
    match = _sample_match()
    assert simulate_result(match) == simulate_result(match)
