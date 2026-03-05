"""Club schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ClubResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    abbreviation: str
    league_id: uuid.UUID | None = None


class ClubUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=64)
    abbreviation: str | None = Field(None, min_length=2, max_length=4)
