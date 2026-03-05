"""Player / squad schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class PlayerSkillsResponse(BaseModel):
    model_config = {"from_attributes": True}

    goalkeeping: float
    defending: float
    midfield: float
    attacking: float
    fitness: float
    set_pieces: float


class PlayerResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    first_name: str
    last_name: str
    age: int
    position: str
    talent: int
    skills: PlayerSkillsResponse | None = None


class SquadResponse(BaseModel):
    model_config = {"from_attributes": True}

    players: list[PlayerResponse] = []
