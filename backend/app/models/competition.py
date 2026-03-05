"""Competition models – leagues, fixtures, results, events."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(128))
    season: Mapped[int] = mapped_column(Integer)
    tier: Mapped[int] = mapped_column(Integer, default=1)


class Fixture(Base):
    __tablename__ = "fixtures"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    league_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    home_club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    away_club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    match_day: Mapped[int] = mapped_column(Integer)
    competition: Mapped[str] = mapped_column(String(16))  # league, cup, ucl
    kickoff: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), default="scheduled")


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fixture_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    home_goals: Mapped[int] = mapped_column(Integer)
    away_goals: Mapped[int] = mapped_column(Integer)
    home_penalty_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_penalty_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seed_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    events_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class MatchEvent(Base):
    __tablename__ = "match_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fixture_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    minute: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(32))  # goal, card, sub, etc.
    team: Mapped[str] = mapped_column(String(8))  # home / away
    detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
