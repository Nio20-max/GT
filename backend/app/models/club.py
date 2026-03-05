"""Club and club-profile models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    abbreviation: Mapped[str] = mapped_column(String(4))
    league_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ClubProfile(Base):
    __tablename__ = "club_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    stadium_name: Mapped[str] = mapped_column(String(128), default="My Stadium")
    stadium_capacity: Mapped[int] = mapped_column(Integer, default=5000)
    morale: Mapped[int] = mapped_column(Integer, default=50)
    sponsor_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sponsor_income: Mapped[int] = mapped_column(Integer, default=0)
