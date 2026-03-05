from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from random import Random

from app.core.config import settings
from app.domain.bots import BotProfile, daily_star_budget, draw_persona
from app.domain.match_engine import MatchInput, TeamVector, simulate_result
from app.domain.training import TrainingContext, daily_gain
from app.services.event_bus import EVENT_BUS
from app.services.persistent_json import JsonStateFile
from app.services.settlement_store import SETTLEMENT_STORE


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
        self._artifacts_by_fixture: dict[int, dict] = {}
        self._state_file = JsonStateFile(settings.state_dir_path / "runtime_state.json")
        if not self._load():
            self._seed_fixtures()
            self._save()

    def _load(self) -> bool:
        payload = self._state_file.load(default={})
        if not isinstance(payload, dict):
            return False

        raw_fixtures = payload.get("fixtures")
        if not isinstance(raw_fixtures, list):
            return False

        parsed: list[Fixture] = []
        for raw in raw_fixtures:
            try:
                parsed.append(Fixture(**raw))
            except Exception:
                continue

        if not parsed:
            return False

        self.season_id = int(payload.get("seasonId", 1))
        self.fixtures = parsed
        self._fixture_counter = max(f.fixture_id for f in parsed)
        raw_artifacts = payload.get("artifactsByFixture", {})
        if isinstance(raw_artifacts, dict):
            normalized: dict[int, dict] = {}
            for key, value in raw_artifacts.items():
                try:
                    fixture_id = int(key)
                except Exception:
                    continue
                if isinstance(value, dict):
                    normalized[fixture_id] = value
            self._artifacts_by_fixture = normalized
        return True

    def _save(self) -> None:
        self._state_file.save(
            {
                "seasonId": self.season_id,
                "fixtureCounter": self._fixture_counter,
                "fixtures": [asdict(fixture) for fixture in self.fixtures],
                "artifactsByFixture": self._artifacts_by_fixture,
            }
        )

    def fixture_by_id(self, fixture_id: int) -> Fixture | None:
        for fixture in self.fixtures:
            if fixture.fixture_id == fixture_id:
                return fixture
        return None

    def fixture_lock_status(self, fixture_id: int) -> dict:
        fixture = self.fixture_by_id(fixture_id)
        if fixture is None:
            return {"fixtureId": fixture_id, "exists": False, "locked": False}
        return {
            "fixtureId": fixture.fixture_id,
            "exists": True,
            "competition": fixture.competition,
            "status": fixture.status,
            "locked": fixture.status != "scheduled",
        }

    def precompute_artifact(self, fixture_id: int) -> dict | None:
        return self._artifacts_by_fixture.get(fixture_id)

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
                server_secret=settings.simulation_server_secret,
                home=TeamVector(70 + fixture.home_team % 10, 68 + fixture.home_team % 8, 66 + fixture.home_team % 7),
                away=TeamVector(70 + fixture.away_team % 10, 68 + fixture.away_team % 8, 66 + fixture.away_team % 7),
            )
            result = simulate_result(match)
            fixture.result_home = result["homeGoals"]
            fixture.result_away = result["awayGoals"]
            frozen_inputs = {
                "competition": fixture.competition,
                "seasonId": fixture.season_id,
                "homeTeam": fixture.home_team,
                "awayTeam": fixture.away_team,
                "seedVersion": match.seed_version,
            }
            checksum = sha256(
                (
                    f"{fixture.fixture_id}|{fixture.competition}|{fixture.season_id}|"
                    f"{fixture.home_team}|{fixture.away_team}|{result['homeGoals']}|{result['awayGoals']}"
                ).encode("utf-8")
            ).hexdigest()
            self._artifacts_by_fixture[fixture.fixture_id] = {
                "fixtureId": fixture.fixture_id,
                "seedVersion": match.seed_version,
                "frozenInputs": frozen_inputs,
                "result": {"homeGoals": result["homeGoals"], "awayGoals": result["awayGoals"]},
                "checksum": checksum,
                "computedAtUtc": datetime.now(timezone.utc).isoformat(),
            }
            fixture.status = "precomputed"
            updated += 1
        if updated:
            self._save()
        return {"competition": competition, "precomputed": updated}

    def run_publish(self, competition: str) -> dict:
        published = 0
        for fixture in self.fixtures:
            if fixture.competition == competition and fixture.status == "precomputed":
                fixture.status = "published"
                settlement = SETTLEMENT_STORE.record_fixture_settlement(
                    {
                        "fixtureId": fixture.fixture_id,
                        "competition": fixture.competition,
                        "seasonId": fixture.season_id,
                        "homeClubId": fixture.home_team,
                        "awayClubId": fixture.away_team,
                        "homeGoals": fixture.result_home,
                        "awayGoals": fixture.result_away,
                    },
                    source="publish",
                )
                EVENT_BUS.publish("match.settled", settlement)
                published += 1
        if published:
            self._save()
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
        self._save()
        return {"newSeasonId": self.season_id, "fixtures": len(self.fixtures)}

    def deep_health(self) -> dict:
        status_counts = Counter(f.status for f in self.fixtures)
        sample = [asdict(f) for f in self.fixtures[:5]]
        return {
            "seasonId": self.season_id,
            "fixturesByStatus": dict(status_counts),
            "sampleFixtures": sample,
            "recentSettlements": SETTLEMENT_STORE.latest(limit=5),
            "timestampUtc": datetime.now(timezone.utc).isoformat(),
        }


RUNTIME_STATE = RuntimeState()
