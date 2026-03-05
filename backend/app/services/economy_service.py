"""Economy service – wallet operations and ledger writes."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class LedgerRecord:
    club_id: uuid.UUID
    amount: int
    currency: str
    reason: str
    description: str | None = None
    created_at: datetime | None = None


def create_ledger_entry(
    club_id: uuid.UUID,
    amount: int,
    currency: str,
    reason: str,
    description: str | None = None,
) -> LedgerRecord:
    """Build a ledger record (DB persistence handled by caller)."""
    return LedgerRecord(
        club_id=club_id,
        amount=amount,
        currency=currency,
        reason=reason,
        description=description,
        created_at=datetime.now(timezone.utc),
    )


def validate_wallet_spend(balance: int, amount: int) -> bool:
    """Return True if the club can afford the spend."""
    return balance >= amount
