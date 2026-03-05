"""Goal Tactics – application settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GT_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # ── Database / Redis ────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://localhost/goaltactics"
    redis_url: str = "redis://localhost:6379/0"

    # ── JWT ──────────────────────────────────────────────────────────────
    jwt_secret: str = "CHANGE-ME-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_minutes: int = 60 * 24 * 7  # 7 days

    # ── Game constants ──────────────────────────────────────────────────
    league_size: int = 12
    starting_money: int = 5_000_000
    starting_stars: int = 20_000

    # ── Schedule (hours in UTC unless noted) ─────────────────────────
    league_kickoff_utc: str = "18:00"
    league_lock_utc: str = "17:00"
    cup_kickoff_utc: str = "13:00"
    cup_lock_utc: str = "12:00"
    training_tick_utc: str = "00:00"
    reports_time: str = "08:00"
    reports_tz: str = "Europe/London"

    # ── Match engine ────────────────────────────────────────────────────
    server_secret: str = "CHANGE-ME-SERVER-SECRET"
    seed_version: int = 1


settings = Settings()
