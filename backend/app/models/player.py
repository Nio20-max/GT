"""Player, skills, and training-state models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    age: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(String(4))  # GK, DEF, MID, ATT
    talent: Mapped[int] = mapped_column(Integer)  # 1-10
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PlayerSkills(Base):
    __tablename__ = "player_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    goalkeeping: Mapped[float] = mapped_column(Float, default=100.0)
    defending: Mapped[float] = mapped_column(Float, default=100.0)
    midfield: Mapped[float] = mapped_column(Float, default=100.0)
    attacking: Mapped[float] = mapped_column(Float, default=100.0)
    fitness: Mapped[float] = mapped_column(Float, default=100.0)
    set_pieces: Mapped[float] = mapped_column(Float, default=100.0)


class PlayerTrainingState(Base):
    __tablename__ = "player_training_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    fatigue: Mapped[float] = mapped_column(Float, default=0.0)
    anti_age_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
