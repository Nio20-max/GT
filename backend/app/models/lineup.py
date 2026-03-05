"""Lineup and tactic models."""

from __future__ import annotations

import uuid

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Lineup(Base):
    __tablename__ = "lineups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    label: Mapped[str] = mapped_column(String(32), default="current")
    formation: Mapped[str] = mapped_column(String(8), default="4-4-2")


class LineupSlot(Base):
    __tablename__ = "lineup_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lineup_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    slot_index: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(8))  # GK, DEF, MID, ATT, SUB


class Tactic(Base):
    __tablename__ = "tactics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True
    )
    tempo: Mapped[str] = mapped_column(String(16), default="normal")
    marking: Mapped[str] = mapped_column(String(16), default="zonal")
    passing: Mapped[str] = mapped_column(String(16), default="mixed")
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
