"""Economy / wallet schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class WalletResponse(BaseModel):
    model_config = {"from_attributes": True}

    club_id: uuid.UUID
    money: int
    stars: int


class LedgerEntry(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    amount: int
    currency: str
    reason: str
    description: str | None = None
    created_at: datetime
