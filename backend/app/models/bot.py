"""Bot profile and behaviour-state models."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BotProfile(Base):
    __tablename__ = "bot_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    difficulty: Mapped[str] = mapped_column(String(16), default="medium")
    personality: Mapped[str] = mapped_column(String(16), default="balanced")


class BotBehaviorState(Base):
    __tablename__ = "bot_behavior_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    bot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    aggression: Mapped[float] = mapped_column(Float, default=0.5)
    transfer_budget_pct: Mapped[float] = mapped_column(Float, default=0.3)
    preferred_formation: Mapped[str] = mapped_column(String(8), default="4-4-2")
    state_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tick: Mapped[int] = mapped_column(Integer, default=0)
