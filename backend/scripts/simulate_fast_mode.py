from __future__ import annotations

from dataclasses import dataclass
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


def run_simulation(seasons: int = 3, clubs_per_league: int = 12) -> dict:
    rng = Random(20260305)
    clubs = [
        Club(
            club_id=i + 1,
            attack=rng.uniform(60, 85),
            midfield=rng.uniform(60, 85),
            defense=rng.uniform(60, 85),
        )
        for i in range(clubs_per_league)
    ]

    total_matches = 0
    upsets = 0
    goals = 0
    training_gain_total = 0.0
    training_samples = 0
    transfer_volume = 0
    scout_discoveries = 0
    bot_budget_total = 0

    for season in range(1, seasons + 1):
        for i in range(len(clubs)):
            for j in range(i + 1, len(clubs)):
                home = clubs[i]
                away = clubs[j]
                total_matches += 1
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
                goals += result["homeGoals"] + result["awayGoals"]
                if (home.attack + home.midfield + home.defense) < (away.attack + away.midfield + away.defense):
                    if result["homeGoals"] > result["awayGoals"]:
                        upsets += 1

                for c in (home, away):
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

                transfer_volume += rng.randint(0, 4)
                scout_discoveries += rng.randint(0, 2)

        for _ in range(clubs_per_league):
            profile = BotProfile("balanced", rng.randint(20, 95), rng.randint(10, 95), rng.randint(0, 100))
            bot_budget_total += daily_star_budget(profile, league_bonus=300, rng=rng)

    avg_goals = goals / max(1, total_matches)
    avg_training_gain = training_gain_total / max(1, training_samples)

    return {
        "seasons": seasons,
        "clubs_per_league": clubs_per_league,
        "matches": total_matches,
        "avg_goals_per_match": round(avg_goals, 3),
        "upset_rate": round(upsets / max(1, total_matches), 4),
        "avg_training_gain": round(avg_training_gain, 4),
        "transfer_volume": transfer_volume,
        "scout_discoveries": scout_discoveries,
        "avg_bot_daily_budget": round(bot_budget_total / max(1, seasons * clubs_per_league), 2),
    }


if __name__ == "__main__":
    print(run_simulation())
