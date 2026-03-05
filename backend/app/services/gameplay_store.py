from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from threading import Lock
from uuid import uuid4

from app.core.config import settings
from app.services.persistent_json import JsonStateFile


@dataclass
class TrainingState:
    style: str = "balanced"
    team_intensity: int = 50


class GameplayStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._rng = Random(20260305)
        self._state_file = JsonStateFile(settings.state_dir_path / "gameplay_state.json")
        self._training_by_user: dict[str, TrainingState] = {}
        self._scouting_results_by_user: dict[str, list[dict]] = {}
        self._auctions: list[dict] = []
        self._favorites_by_user: dict[str, list[str]] = {}
        self._bids_by_user: dict[str, list[dict]] = {}
        self._load()
        if not self._auctions:
            self._seed_auctions()
            self._save()

    def _load(self) -> None:
        payload = self._state_file.load(
            default={
                "trainingByUser": {},
                "scoutingResultsByUser": {},
                "auctions": [],
                "favoritesByUser": {},
                "bidsByUser": {},
            }
        )
        if not isinstance(payload, dict):
            return

        training = payload.get("trainingByUser", {})
        if isinstance(training, dict):
            for user_id, raw in training.items():
                if not isinstance(raw, dict):
                    continue
                try:
                    self._training_by_user[str(user_id)] = TrainingState(**raw)
                except Exception:
                    continue

        scouting = payload.get("scoutingResultsByUser", {})
        if isinstance(scouting, dict):
            self._scouting_results_by_user = {
                str(user_id): [row for row in rows if isinstance(row, dict)]
                for user_id, rows in scouting.items()
                if isinstance(rows, list)
            }

        auctions = payload.get("auctions", [])
        if isinstance(auctions, list):
            self._auctions = [row for row in auctions if isinstance(row, dict)]

        favorites = payload.get("favoritesByUser", {})
        if isinstance(favorites, dict):
            self._favorites_by_user = {
                str(user_id): [str(auction_id) for auction_id in rows]
                for user_id, rows in favorites.items()
                if isinstance(rows, list)
            }

        bids = payload.get("bidsByUser", {})
        if isinstance(bids, dict):
            self._bids_by_user = {
                str(user_id): [row for row in rows if isinstance(row, dict)]
                for user_id, rows in bids.items()
                if isinstance(rows, list)
            }

    def _save(self) -> None:
        self._state_file.save(
            {
                "trainingByUser": {k: asdict(v) for k, v in self._training_by_user.items()},
                "scoutingResultsByUser": self._scouting_results_by_user,
                "auctions": self._auctions,
                "favoritesByUser": self._favorites_by_user,
                "bidsByUser": self._bids_by_user,
            }
        )

    def _seed_auctions(self) -> None:
        self._auctions = []
        for idx in range(1, 25):
            self._auctions.append(
                {
                    "auctionId": str(idx),
                    "playerName": f"Transfer Prospect {idx:02d}",
                    "position": self._rng.choice(["Defender", "Midfielder", "Attacker", "Goalkeeper"]),
                    "strength": round(self._rng.uniform(65, 84), 2),
                    "currentBid": self._rng.randint(70000, 320000),
                }
            )

    def training_state(self, user_id: str) -> TrainingState:
        with self._lock:
            return self._training_by_user.get(user_id, TrainingState())

    def set_training_state(self, user_id: str, style: str, intensity: int) -> TrainingState:
        with self._lock:
            state = TrainingState(style=style, team_intensity=max(0, min(100, intensity)))
            self._training_by_user[user_id] = state
            self._save()
            return state

    def create_scouting_result(self, user_id: str) -> dict:
        with self._lock:
            result = {
                "resultId": str(uuid4()),
                "name": f"Scout Player {self._rng.randint(100, 999)}",
                "age": self._rng.randint(15, 23),
                "talent": self._rng.randint(4, 10),
                "strength": round(self._rng.uniform(58, 82), 2),
            }
            self._scouting_results_by_user.setdefault(user_id, []).append(result)
            self._save()
            return result

    def scouting_results(self, user_id: str) -> list[dict]:
        with self._lock:
            return list(self._scouting_results_by_user.get(user_id, []))

    def sign_scouting_result(self, user_id: str, result_id: str) -> dict | None:
        with self._lock:
            results = self._scouting_results_by_user.get(user_id, [])
            for result in results:
                if str(result.get("resultId")) == result_id:
                    signed = dict(result)
                    signed["signed"] = True
                    return signed
            return None

    def auctions(self) -> list[dict]:
        with self._lock:
            return list(self._auctions)

    def auction(self, auction_id: str) -> dict | None:
        with self._lock:
            for auction in self._auctions:
                if str(auction.get("auctionId")) == auction_id:
                    return dict(auction)
            return None

    def bid(self, user_id: str, auction_id: str, amount: int) -> dict | None:
        with self._lock:
            for auction in self._auctions:
                if str(auction.get("auctionId")) != auction_id:
                    continue
                auction["currentBid"] = max(int(auction.get("currentBid", 0)) + 1, amount)
                bid = {"auctionId": auction_id, "amount": auction["currentBid"]}
                self._bids_by_user.setdefault(user_id, []).append(bid)
                self._save()
                return dict(auction)
            return None

    def bids_for_user(self, user_id: str) -> list[dict]:
        with self._lock:
            return list(self._bids_by_user.get(user_id, []))

    def favorite(self, user_id: str, auction_id: str, enabled: bool) -> list[str]:
        with self._lock:
            favorites = self._favorites_by_user.setdefault(user_id, [])
            if enabled and auction_id not in favorites:
                favorites.append(auction_id)
            if not enabled:
                favorites = [item for item in favorites if item != auction_id]
                self._favorites_by_user[user_id] = favorites
            self._save()
            return list(favorites)

    def favorites_for_user(self, user_id: str) -> list[str]:
        with self._lock:
            return list(self._favorites_by_user.get(user_id, []))


GAMEPLAY_STORE = GameplayStore()
