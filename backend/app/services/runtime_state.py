from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from random import Random

from app.domain.bots import BotProfile, daily_star_budget, draw_persona
from app.domain.match_engine import MatchInput, TeamVector, simulate_result
from app.domain.training import TrainingContext, daily_gain


@dataclass
class Fixture:
    fixture_id: int
    competition: str
    season_id: int
    home_team: int
    away_team: int
    status: str = "scheduled"
    result_home: int | None = None
    result_away: int | None = None


class RuntimeState:
    def __init__(self) -> None:
        self.rng = Random(20260305)
        self.season_id = 1
        self.fixtures: list[Fixture] = []
        self._fixture_counter = 0
        self._seed_fixtures()

    def _seed_fixtures(self, leagues: int = 2, clubs_per_league: int = 12) -> None:
        self.fixtures.clear()
        self._fixture_counter = 0
        for league in range(leagues):
            start_team = league * clubs_per_league + 1
            teams = list(range(start_team, start_team + clubs_per_league))
            for i in range(0, len(teams), 2):
                self._fixture_counter += 1
                self.fixtures.append(
                    Fixture(
                        fixture_id=self._fixture_counter,
                        competition="league",
                        season_id=self.season_id,
                        home_team=teams[i],
                        away_team=teams[i + 1],
                    )
                )

        for comp in ("cup", "ucl"):
            for _ in range(6):
                home = self.rng.randint(1, leagues * clubs_per_league)
                away = self.rng.randint(1, leagues * clubs_per_league)
                if home == away:
                    away = max(1, (away % (leagues * clubs_per_league)) + 1)
                self._fixture_counter += 1
                self.fixtures.append(
                    Fixture(
                        fixture_id=self._fixture_counter,
                        competition=comp,
                        season_id=self.season_id,
                        home_team=home,
                        away_team=away,
                    )
                )

    def runtime_calendar(self) -> dict:
        return {
            "league": {"lockUtc": "17:00", "kickoffUtc": "18:00"},
            "cupUcl": {"lockUtc": "12:00", "kickoffUtc": "13:00"},
            "friendly": {"lockUtc": "12:00", "kickoffUtc": "13:00"},
            "trainingTickUtc": "00:00",
            "reportDispatchTz": "Europe/London",
            "reportDispatchLocal": "08:00",
        }

    def runtime_locks(self) -> dict:
        scheduled = sum(1 for f in self.fixtures if f.status == "scheduled")
        precomputed = sum(1 for f in self.fixtures if f.status == "precomputed")
        published = sum(1 for f in self.fixtures if f.status == "published")
        return {
            "scheduled": scheduled,
            "precomputed": precomputed,
            "published": published,
            "timestampUtc": datetime.now(timezone.utc).isoformat(),
        }

    def run_precompute(self, competition: str) -> dict:
        updated = 0
        for fixture in self.fixtures:
            if fixture.competition != competition or fixture.status != "scheduled":
                continue
            match = MatchInput(
                match_id=fixture.fixture_id,
                competition=fixture.competition,
                season_id=fixture.season_id,
                seed_version=1,
                server_secret="gt-server-secret",
                home=TeamVector(70 + fixture.home_team % 10, 68 + fixture.home_team % 8, 66 + fixture.home_team % 7),
                away=TeamVector(70 + fixture.away_team % 10, 68 + fixture.away_team % 8, 66 + fixture.away_team % 7),
            )
            result = simulate_result(match)
            fixture.result_home = result["homeGoals"]
            fixture.result_away = result["awayGoals"]
            fixture.status = "precomputed"
            updated += 1
        return {"competition": competition, "precomputed": updated}

    def run_publish(self, competition: str) -> dict:
        published = 0
        for fixture in self.fixtures:
            if fixture.competition == competition and fixture.status == "precomputed":
                fixture.status = "published"
                published += 1
        return {"competition": competition, "published": published}

    def run_training_tick(self, sample_players: int = 800) -> dict:
        total_gain = 0.0
        for _ in range(sample_players):
            gain = daily_gain(
                TrainingContext(
                    age=self.rng.randint(16, 34),
                    strength=self.rng.uniform(120, 920),
                    talent=self.rng.randint(1, 10),
                    style=self.rng.choice(["conservative", "balanced", "aggressive"]),
                    skill_bucket=self.rng.choice(["goalkeeper", "defense", "midfield", "attack"]),
                    fatigue=self.rng.uniform(0, 80),
                )
            )
            total_gain += gain
        return {
            "samplePlayers": sample_players,
            "avgGain": round(total_gain / max(1, sample_players), 4),
        }

    def run_bot_cycle(self, bot_count: int = 120) -> dict:
        persona_counts: Counter[str] = Counter()
        budget_total = 0
        for _ in range(bot_count):
            persona = draw_persona(self.rng)
            persona_counts[persona] += 1
            profile = BotProfile(
                persona=persona,
                activeness=self.rng.randint(20, 95),
                star_buyer=self.rng.randint(10, 95),
                alliance_loyalty=self.rng.randint(0, 100),
            )
            budget_total += daily_star_budget(profile, league_bonus=300, rng=self.rng)

        return {
            "botCount": bot_count,
            "avgBudget": round(budget_total / max(1, bot_count), 2),
            "personas": dict(persona_counts),
        }

    def run_transfer_injections(self) -> dict:
        amount = self.rng.randint(50000, 250000)
        return {"seasonId": self.season_id, "injectedStars": amount}

    def run_ticks(self) -> dict:
        return {
            "precomputeLeague": self.run_precompute("league"),
            "publishLeague": self.run_publish("league"),
            "trainingTick": self.run_training_tick(),
            "botCycle": self.run_bot_cycle(),
        }

    def rollover(self) -> dict:
        self.season_id += 1
        self._seed_fixtures()
        return {"newSeasonId": self.season_id, "fixtures": len(self.fixtures)}

    def deep_health(self) -> dict:
        status_counts = Counter(f.status for f in self.fixtures)
        sample = [asdict(f) for f in self.fixtures[:5]]
        return {
            "seasonId": self.season_id,
            "fixturesByStatus": dict(status_counts),
            "sampleFixtures": sample,
            "timestampUtc": datetime.now(timezone.utc).isoformat(),
        }


RUNTIME_STATE = RuntimeState()
