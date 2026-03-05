from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from threading import Lock
from uuid import uuid4

from app.core.config import settings
from app.services.auth_store import UserRecord
from app.services.pg_repo import pg_cursor, pg_enabled
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
        self._pg_failed = False
        self._rng = Random(20260305)
        self._clubs_by_user: dict[str, ClubRecord] = {}
        self._players_by_club: dict[str, list[PlayerRecord]] = {}
        self._state_file = JsonStateFile(settings.state_dir_path / "game_state.json")
        self._load()

    def _can_use_pg(self) -> bool:
        return pg_enabled() and not self._pg_failed

    def _load(self) -> None:
        if self._can_use_pg():
            self._load_from_pg()
            return
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
        if self._can_use_pg():
            return
        payload = {
            "clubs": [asdict(club) for club in self._clubs_by_user.values()],
            "playersByClub": {
                club_id: [asdict(player) for player in players]
                for club_id, players in self._players_by_club.items()
            },
        }
        self._state_file.save(payload)

    def _load_from_pg(self) -> None:
        try:
            with pg_cursor() as cur:
                cur.execute("SELECT id::text, user_id::text, name, money, stars FROM clubs")
                for row in cur.fetchall():
                    club_id, user_id, name, money, stars = row
                    self._clubs_by_user[str(user_id)] = ClubRecord(
                        club_id=str(club_id),
                        user_id=str(user_id),
                        name=str(name),
                        money=int(money),
                        stars=int(stars),
                        league_id=1,
                    )

                cur.execute("SELECT id::text, club_id::text, name, age, strength, talent, position FROM players")
                for row in cur.fetchall():
                    player_id, club_id, name, age, strength, talent, position = row
                    self._players_by_club.setdefault(str(club_id), []).append(
                        PlayerRecord(
                            player_id=str(player_id),
                            club_id=str(club_id),
                            name=str(name),
                            age=int(age),
                            strength=float(strength),
                            talent=int(talent),
                            position=str(position),
                        )
                    )
        except Exception:
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
            if self._can_use_pg():
                try:
                    with pg_cursor() as cur:
                        cur.execute(
                            "INSERT INTO clubs (user_id, name, money, stars) VALUES (%s::bigint, %s, %s, %s) RETURNING id",
                            (user.user_id, club.name, club.money, club.stars),
                        )
                        row = cur.fetchone()
                        if row is not None:
                            club.club_id = str(row[0])
                        players = self._starter_squad(club.club_id)
                        self._players_by_club[club.club_id] = players
                        for player in players:
                            cur.execute(
                                "INSERT INTO players (club_id, name, age, strength, talent, position) VALUES (%s::bigint, %s, %s, %s, %s, %s) RETURNING id",
                                (club.club_id, player.name, player.age, player.strength, player.talent, player.position),
                            )
                            prow = cur.fetchone()
                            if prow is not None:
                                player.player_id = str(prow[0])
                except Exception:
                    self._pg_failed = True
                    self._players_by_club[club.club_id] = self._starter_squad(club.club_id)
            else:
                self._players_by_club[club.club_id] = self._starter_squad(club.club_id)

            self._clubs_by_user[user.user_id] = club
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

    def player_for_user(self, user_id: str, player_id: str) -> PlayerRecord | None:
        with self._lock:
            club = self._clubs_by_user.get(user_id)
            if club is None:
                return None
            for player in self._players_by_club.get(club.club_id, []):
                if player.player_id == player_id:
                    return player
            return None

    def update_player_for_user(self, user_id: str, player: PlayerRecord) -> bool:
        with self._lock:
            club = self._clubs_by_user.get(user_id)
            if club is None:
                return False
            players = self._players_by_club.get(club.club_id, [])
            for idx, existing in enumerate(players):
                if existing.player_id == player.player_id:
                    players[idx] = player
                    if self._can_use_pg():
                        try:
                            with pg_cursor() as cur:
                                cur.execute(
                                    "UPDATE players SET name=%s, age=%s, strength=%s, talent=%s, position=%s WHERE id=%s::bigint",
                                    (player.name, player.age, player.strength, player.talent, player.position, player.player_id),
                                )
                        except Exception:
                            self._pg_failed = True
                    self._save()
                    return True
            return False

    def remove_player_for_user(self, user_id: str, player_id: str) -> bool:
        with self._lock:
            club = self._clubs_by_user.get(user_id)
            if club is None:
                return False
            players = self._players_by_club.get(club.club_id, [])
            next_players = [p for p in players if p.player_id != player_id]
            if len(next_players) == len(players):
                return False
            self._players_by_club[club.club_id] = next_players
            if self._can_use_pg():
                try:
                    with pg_cursor() as cur:
                        cur.execute("DELETE FROM players WHERE id=%s::bigint", (player_id,))
                except Exception:
                    self._pg_failed = True
            self._save()
            return True

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
            # New managers should start with a playable but improvable squad around 70 rating.
            strength = round(self._rng.uniform(64, 76), 2)
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
