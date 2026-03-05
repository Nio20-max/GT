from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from random import Random
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.domain.bots import BotProfile, daily_star_budget
from app.domain.match_engine import MatchInput, TeamVector, simulate_result
from app.domain.training import TrainingContext, daily_gain


@dataclass
class Club:
    club_id: int
    attack: float
    midfield: float
    defense: float


def run_simulation(seasons: int = 3, leagues: int = 1, clubs_per_league: int = 12) -> dict:
    rng = Random(20260305)
    leagues_clubs = [
        [
            Club(
                club_id=(league * clubs_per_league) + i + 1,
                attack=rng.uniform(60, 85),
                midfield=rng.uniform(60, 85),
                defense=rng.uniform(60, 85),
            )
            for i in range(clubs_per_league)
        ]
        for league in range(leagues)
    ]

    season_summaries: list[dict] = []

    total_matches = 0
    upsets = 0
    goals = 0
    training_gain_total = 0.0
    training_samples = 0
    transfer_volume = 0
    scout_discoveries = 0
    bot_budget_total = 0

    for season in range(1, seasons + 1):
        season_matches = 0
        season_goals = 0
        season_upsets = 0
        season_transfer_volume = 0
        season_scout_discoveries = 0

        for clubs in leagues_clubs:
            for i in range(len(clubs)):
                for j in range(i + 1, len(clubs)):
                    home = clubs[i]
                    away = clubs[j]
                    total_matches += 1
                    season_matches += 1
                    result = simulate_result(
                        MatchInput(
                            match_id=season * 100000 + total_matches,
                            competition="league",
                            season_id=season,
                            seed_version=1,
                            server_secret="gt-server-secret",
                            home=TeamVector(home.attack, home.midfield, home.defense),
                            away=TeamVector(away.attack, away.midfield, away.defense),
                        )
                    )
                    match_goals = result["homeGoals"] + result["awayGoals"]
                    goals += match_goals
                    season_goals += match_goals
                    if (
                        home.attack + home.midfield + home.defense
                    ) < (away.attack + away.midfield + away.defense):
                        if result["homeGoals"] > result["awayGoals"]:
                            upsets += 1
                            season_upsets += 1

                    for _ in (home, away):
                        gain = daily_gain(
                            TrainingContext(
                                age=rng.randint(18, 34),
                                strength=rng.uniform(120, 900),
                                talent=rng.randint(1, 10),
                                style=rng.choice(["conservative", "balanced", "aggressive"]),
                                skill_bucket=rng.choice(["goalkeeper", "defense", "midfield", "attack"]),
                                fatigue=rng.uniform(0, 80),
                            )
                        )
                        training_gain_total += gain
                        training_samples += 1

                    tv = rng.randint(0, 4)
                    sd = rng.randint(0, 2)
                    transfer_volume += tv
                    scout_discoveries += sd
                    season_transfer_volume += tv
                    season_scout_discoveries += sd

        for _ in range(leagues * clubs_per_league):
            profile = BotProfile(
                "balanced",
                rng.randint(20, 95),
                rng.randint(10, 95),
                rng.randint(0, 100),
            )
            bot_budget_total += daily_star_budget(profile, league_bonus=300, rng=rng)

        season_summaries.append(
            {
                "season": season,
                "matches": season_matches,
                "avg_goals_per_match": round(season_goals / max(1, season_matches), 3),
                "upset_rate": round(season_upsets / max(1, season_matches), 4),
                "transfer_volume": season_transfer_volume,
                "scout_discoveries": season_scout_discoveries,
            }
        )

    avg_goals = goals / max(1, total_matches)
    avg_training_gain = training_gain_total / max(1, training_samples)

    return {
        "seasons": seasons,
        "leagues": leagues,
        "clubs_per_league": clubs_per_league,
        "matches": total_matches,
        "avg_goals_per_match": round(avg_goals, 3),
        "upset_rate": round(upsets / max(1, total_matches), 4),
        "avg_training_gain": round(avg_training_gain, 4),
        "transfer_volume": transfer_volume,
        "scout_discoveries": scout_discoveries,
        "avg_bot_daily_budget": round(bot_budget_total / max(1, seasons * clubs_per_league * leagues), 2),
        "season_summaries": season_summaries,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GT fast deterministic simulation")
    parser.add_argument("--seasons", type=int, default=3)
    parser.add_argument("--leagues", type=int, default=1)
    parser.add_argument("--clubs-per-league", type=int, default=12)
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    result = run_simulation(
        seasons=max(1, args.seasons),
        leagues=max(1, args.leagues),
        clubs_per_league=max(4, args.clubs_per_league),
    )
    payload = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    print(payload)
