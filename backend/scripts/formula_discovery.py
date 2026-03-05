from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.domain.training import TrainingContext, daily_gain


def run() -> list[dict[str, float | int | str]]:
    scenarios = [
        TrainingContext(18, 120, 8, "balanced", "midfield", fatigue=10),
        TrainingContext(22, 300, 7, "aggressive", "attack", fatigue=15),
        TrainingContext(25, 550, 6, "balanced", "defense", fatigue=25),
        TrainingContext(29, 680, 5, "conservative", "goalkeeper", fatigue=35),
        TrainingContext(31, 760, 6, "balanced", "midfield", fatigue=45),
        TrainingContext(34, 900, 4, "conservative", "defense", fatigue=70),
    ]
    rows = []
    for s in scenarios:
        rows.append(
            {
                "age": s.age,
                "strength": s.strength,
                "talent": s.talent,
                "style": s.style,
                "bucket": s.skill_bucket,
                "fatigue": s.fatigue,
                "daily_gain": round(daily_gain(s), 4),
            }
        )
    return rows


if __name__ == "__main__":
    for row in run():
        print(row)
