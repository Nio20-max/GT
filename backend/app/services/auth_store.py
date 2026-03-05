from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from uuid import uuid4

from app.core.config import settings
from app.services.pg_repo import pg_cursor, pg_enabled
from app.services.persistent_json import JsonStateFile


@dataclass
class UserRecord:
    user_id: str
    username: str
    email: str
    password_hash: str


@dataclass
class TokenRecord:
    user_id: str
    expires_at: datetime


class AuthStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._pg_failed = False
        self._users_by_username: dict[str, UserRecord] = {}
        self._tokens: dict[str, TokenRecord] = {}
        self._state_file = JsonStateFile(settings.state_dir_path / "auth_state.json")
        self._load()

    def _can_use_pg(self) -> bool:
        return pg_enabled() and not self._pg_failed

    def _load(self) -> None:
        if self._can_use_pg():
            self._load_from_pg()
            return
        payload = self._state_file.load(default={"users": [], "tokens": {}})
        users = payload.get("users", []) if isinstance(payload, dict) else []
        tokens = payload.get("tokens", {}) if isinstance(payload, dict) else {}

        if isinstance(users, list):
            for raw in users:
                try:
                    record = UserRecord(**raw)
                    self._users_by_username[record.username] = record
                except Exception:
                    continue

        if isinstance(tokens, dict):
            for token, raw in tokens.items():
                try:
                    expires_at = datetime.fromisoformat(raw["expires_at"])
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    self._tokens[token] = TokenRecord(user_id=raw["user_id"], expires_at=expires_at)
                except Exception:
                    continue

    def _reload_from_json_state(self) -> None:
        payload = self._state_file.load(default={"users": [], "tokens": {}})
        users = payload.get("users", []) if isinstance(payload, dict) else []
        tokens = payload.get("tokens", {}) if isinstance(payload, dict) else {}

        if isinstance(users, list):
            for raw in users:
                try:
                    record = UserRecord(**raw)
                    self._users_by_username[record.username] = record
                except Exception:
                    continue

        if isinstance(tokens, dict):
            for token, raw in tokens.items():
                try:
                    expires_at = datetime.fromisoformat(raw["expires_at"])
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    self._tokens[token] = TokenRecord(user_id=raw["user_id"], expires_at=expires_at)
                except Exception:
                    continue

    def _save(self) -> None:
        if self._can_use_pg():
            return
        payload = {
            "users": [record.__dict__ for record in self._users_by_username.values()],
            "tokens": {
                token: {"user_id": record.user_id, "expires_at": record.expires_at.isoformat()}
                for token, record in self._tokens.items()
            },
        }
        self._state_file.save(payload)

    def _load_from_pg(self) -> None:
        try:
            with pg_cursor() as cur:
                cur.execute("SELECT id::text, username, email, password_hash FROM users")
                for row in cur.fetchall():
                    user_id, username, email, password_hash = row
                    self._users_by_username[str(username)] = UserRecord(
                        user_id=str(user_id),
                        username=str(username),
                        email=str(email),
                        password_hash=str(password_hash),
                    )
                cur.execute("SELECT token, user_id::text, expires_at FROM sessions")
                for row in cur.fetchall():
                    token, user_id, expires_at = row
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    self._tokens[str(token)] = TokenRecord(user_id=str(user_id), expires_at=expires_at)
        except Exception:
            payload = self._state_file.load(default={"users": [], "tokens": {}})
            users = payload.get("users", []) if isinstance(payload, dict) else []
            tokens = payload.get("tokens", {}) if isinstance(payload, dict) else {}
            if isinstance(users, list):
                for raw in users:
                    try:
                        record = UserRecord(**raw)
                        self._users_by_username[record.username] = record
                    except Exception:
                        continue
            if isinstance(tokens, dict):
                for token, raw in tokens.items():
                    try:
                        expires_at = datetime.fromisoformat(raw["expires_at"])
                        if expires_at.tzinfo is None:
                            expires_at = expires_at.replace(tzinfo=timezone.utc)
                        self._tokens[token] = TokenRecord(user_id=raw["user_id"], expires_at=expires_at)
                    except Exception:
                        continue

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        iterations = 390000
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        try:
            algorithm, iteration_raw, salt_hex, digest_hex = password_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            iterations = int(iteration_raw)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                iterations,
            )
            return hmac.compare_digest(digest.hex(), digest_hex)
        except Exception:
            return False

    def _purge_expired_tokens(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [token for token, record in self._tokens.items() if record.expires_at <= now]
        for token in expired:
            del self._tokens[token]
        if expired and self._can_use_pg():
            try:
                with pg_cursor() as cur:
                    for token in expired:
                        cur.execute("DELETE FROM sessions WHERE token=%s", (token,))
            except Exception:
                self._pg_failed = True
        if expired:
            self._save()

    def register(self, username: str, email: str, password: str) -> UserRecord:
        with self._lock:
            self._purge_expired_tokens()
            if username in self._users_by_username:
                raise ValueError("username already exists")
            record = UserRecord(
                user_id=str(uuid4()),
                username=username,
                email=email,
                password_hash=self._hash_password(password),
            )
            if self._can_use_pg():
                try:
                    with pg_cursor() as cur:
                        cur.execute(
                            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                            (record.username, record.email, record.password_hash),
                        )
                        row = cur.fetchone()
                        if row is not None:
                            record.user_id = str(row[0])
                except Exception:
                    self._pg_failed = True
            self._users_by_username[username] = record
            self._save()
            return record

    def login(self, username: str, password: str) -> tuple[UserRecord, str]:
        with self._lock:
            self._purge_expired_tokens()
            record = self._users_by_username.get(username)
            if record is None:
                raise ValueError("invalid credentials")
            if not self._verify_password(password, record.password_hash):
                raise ValueError("invalid credentials")
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.auth_token_ttl_seconds)
            self._tokens[token] = TokenRecord(user_id=record.user_id, expires_at=expires_at)
            if self._can_use_pg():
                try:
                    with pg_cursor() as cur:
                        cur.execute(
                            "INSERT INTO sessions (token, user_id, expires_at) VALUES (%s, %s::bigint, %s)",
                            (token, record.user_id, expires_at),
                        )
                except Exception:
                    self._pg_failed = True
            self._save()
            return record, token

    def from_token(self, token: str) -> UserRecord | None:
        with self._lock:
            self._purge_expired_tokens()
            token_record = self._tokens.get(token)
            if token_record is None and self._can_use_pg():
                try:
                    with pg_cursor() as cur:
                        cur.execute("SELECT user_id::text, expires_at FROM sessions WHERE token=%s", (token,))
                        row = cur.fetchone()
                        if row is not None:
                            user_id, expires_at = row
                            if expires_at.tzinfo is None:
                                expires_at = expires_at.replace(tzinfo=timezone.utc)
                            token_record = TokenRecord(user_id=str(user_id), expires_at=expires_at)
                            self._tokens[token] = token_record
                except Exception:
                    self._pg_failed = True
                    token_record = None
            if token_record is None and not self._can_use_pg():
                self._reload_from_json_state()
                token_record = self._tokens.get(token)
            if token_record is None:
                return None
            for user in self._users_by_username.values():
                if user.user_id == token_record.user_id:
                    return user
            if self._can_use_pg():
                try:
                    with pg_cursor() as cur:
                        cur.execute(
                            "SELECT id::text, username, email, password_hash FROM users WHERE id=%s::bigint",
                            (token_record.user_id,),
                        )
                        row = cur.fetchone()
                        if row is not None:
                            user_id, username, email, password_hash = row
                            user = UserRecord(
                                user_id=str(user_id),
                                username=str(username),
                                email=str(email),
                                password_hash=str(password_hash),
                            )
                            self._users_by_username[user.username] = user
                            return user
                except Exception:
                    self._pg_failed = True
                    return None
            else:
                self._reload_from_json_state()
                for user in self._users_by_username.values():
                    if user.user_id == token_record.user_id:
                        return user
            return None

    def from_user_id(self, user_id: str) -> UserRecord | None:
        with self._lock:
            for user in self._users_by_username.values():
                if user.user_id == user_id:
                    return user
            return None


AUTH_STORE = AuthStore()
