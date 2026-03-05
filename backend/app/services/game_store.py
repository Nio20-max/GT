from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from threading import Lock
from uuid import uuid4

from app.core.config import settings
from app.services.auth_store import UserRecord
from app.services.persistent_json import JsonStateFile


@dataclass
class ClubRecord:
    club_id: str
    user_id: str
    name: str
    money: int
    stars: int
    league_id: int


@dataclass
class PlayerRecord:
    player_id: str
    club_id: str
    name: str
    age: int
    strength: float
    talent: int
    position: str


class GameStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._rng = Random(20260305)
        self._clubs_by_user: dict[str, ClubRecord] = {}
        self._players_by_club: dict[str, list[PlayerRecord]] = {}
        self._state_file = JsonStateFile(settings.state_dir_path / "game_state.json")
        self._load()

    def _load(self) -> None:
        payload = self._state_file.load(default={"clubs": [], "playersByClub": {}})
        clubs = payload.get("clubs", []) if isinstance(payload, dict) else []
        players_by_club = payload.get("playersByClub", {}) if isinstance(payload, dict) else {}

        for raw in clubs:
            try:
                record = ClubRecord(**raw)
                self._clubs_by_user[record.user_id] = record
            except Exception:
                continue

        if isinstance(players_by_club, dict):
            for club_id, player_list in players_by_club.items():
                parsed: list[PlayerRecord] = []
                if not isinstance(player_list, list):
                    continue
                for raw_player in player_list:
                    try:
                        parsed.append(PlayerRecord(**raw_player))
                    except Exception:
                        continue
                if parsed:
                    self._players_by_club[club_id] = parsed

    def _save(self) -> None:
        payload = {
            "clubs": [asdict(club) for club in self._clubs_by_user.values()],
            "playersByClub": {
                club_id: [asdict(player) for player in players]
                for club_id, players in self._players_by_club.items()
            },
        }
        self._state_file.save(payload)

    def ensure_user_game_state(self, user: UserRecord) -> ClubRecord:
        with self._lock:
            existing = self._clubs_by_user.get(user.user_id)
            if existing is not None:
                return existing

            club = ClubRecord(
                club_id=str(uuid4()),
                user_id=user.user_id,
                name=f"{user.username.title()} FC",
                money=5000000,
                stars=20000,
                league_id=1,
            )
            self._clubs_by_user[user.user_id] = club
            self._players_by_club[club.club_id] = self._starter_squad(club.club_id)
            self._save()
            return club

    def club_for_user(self, user_id: str) -> ClubRecord | None:
        with self._lock:
            return self._clubs_by_user.get(user_id)

    def squad_for_user(self, user_id: str) -> list[PlayerRecord]:
        with self._lock:
            club = self._clubs_by_user.get(user_id)
            if club is None:
                return []
            players = self._players_by_club.get(club.club_id, [])
            return list(players)

    def _starter_squad(self, club_id: str) -> list[PlayerRecord]:
        players: list[PlayerRecord] = []
        roles = [
            ("GK", "Goalkeeper"),
            ("CB", "Defender"),
            ("CB", "Defender"),
            ("LB", "Defender"),
            ("RB", "Defender"),
            ("CM", "Midfielder"),
            ("CM", "Midfielder"),
            ("LW", "Attacker"),
            ("RW", "Attacker"),
            ("ST", "Attacker"),
            ("ST", "Attacker"),
            ("SUB", "Midfielder"),
            ("SUB", "Defender"),
            ("SUB", "Attacker"),
            ("SUB", "Goalkeeper"),
            ("SUB", "Midfielder"),
        ]

        for index, (short, position) in enumerate(roles, start=1):
            strength = round(self._rng.uniform(210, 410), 2)
            players.append(
                PlayerRecord(
                    player_id=str(uuid4()),
                    club_id=club_id,
                    name=f"Player {index:02d} {short}",
                    age=self._rng.randint(17, 31),
                    strength=strength,
                    talent=self._rng.randint(3, 8),
                    position=position,
                )
            )
        return players


GAME_STORE = GameStore()
