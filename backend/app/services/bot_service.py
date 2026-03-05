"""Bot behaviour service – placeholder logic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BotDecision:
    action: str
    params: dict


def decide_bot_action(difficulty: str, personality: str, tick: int) -> BotDecision:
    """Return the next action a bot club should take.

    This is a simplified stub; real implementation will evaluate club state,
    opponent strength, transfer market, etc.
    """
    if tick % 7 == 0:
        return BotDecision(action="train", params={"style": personality})
    if tick % 14 == 0:
        return BotDecision(action="scout", params={"region": "europe"})
    return BotDecision(action="idle", params={})
