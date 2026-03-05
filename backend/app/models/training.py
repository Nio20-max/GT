"""Training-related models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TeamTraining(Base):
    __tablename__ = "team_trainings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    style: Mapped[str] = mapped_column(String(16), default="balanced")
    focus_skill: Mapped[str] = mapped_column(String(16), default="defending")


class IndividualTraining(Base):
    __tablename__ = "individual_trainings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    focus_skill: Mapped[str] = mapped_column(String(16))
    intensity: Mapped[float] = mapped_column(Float, default=1.0)


class TrainingCamp(Base):
    __tablename__ = "training_camps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TrainingTickAudit(Base):
    __tablename__ = "training_tick_audits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    skill: Mapped[str] = mapped_column(String(16))
    old_value: Mapped[float] = mapped_column(Float)
    new_value: Mapped[float] = mapped_column(Float)
    gain: Mapped[float] = mapped_column(Float)
    decay: Mapped[float] = mapped_column(Float, default=0.0)
    tick_day: Mapped[int] = mapped_column(Integer)
