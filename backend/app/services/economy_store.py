from __future__ import annotations

from dataclasses import asdict, dataclass
from threading import Lock
from uuid import uuid4

from app.core.config import settings
from app.services.persistent_json import JsonStateFile


@dataclass
class Wallet:
    money: int
    stars: int
    medipacks: int = 0


class EconomyStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._state_file = JsonStateFile(settings.state_dir_path / "economy_state.json")
        self._wallet_by_user: dict[str, Wallet] = {}
        self._ledger_by_user: dict[str, list[dict]] = {}
        self._idempotency_index: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        payload = self._state_file.load(default={"walletByUser": {}, "ledgerByUser": {}, "idempotency": {}})
        if not isinstance(payload, dict):
            return
        wallets = payload.get("walletByUser", {})
        if isinstance(wallets, dict):
            for user_id, raw in wallets.items():
                if not isinstance(raw, dict):
                    continue
                try:
                    self._wallet_by_user[str(user_id)] = Wallet(**raw)
                except Exception:
                    continue
        ledger = payload.get("ledgerByUser", {})
        if isinstance(ledger, dict):
            self._ledger_by_user = {
                str(user_id): [entry for entry in entries if isinstance(entry, dict)]
                for user_id, entries in ledger.items()
                if isinstance(entries, list)
            }
        idem = payload.get("idempotency", {})
        if isinstance(idem, dict):
            self._idempotency_index = {str(k): v for k, v in idem.items() if isinstance(v, dict)}

    def _save(self) -> None:
        self._state_file.save(
            {
                "walletByUser": {user_id: asdict(wallet) for user_id, wallet in self._wallet_by_user.items()},
                "ledgerByUser": self._ledger_by_user,
                "idempotency": self._idempotency_index,
            }
        )

    def wallet(self, user_id: str) -> Wallet:
        with self._lock:
            wallet = self._wallet_by_user.get(user_id)
            if wallet is None:
                wallet = Wallet(money=5000000, stars=20000, medipacks=0)
                self._wallet_by_user[user_id] = wallet
                self._save()
            return wallet

    def ledger(self, user_id: str) -> list[dict]:
        with self._lock:
            return list(self._ledger_by_user.get(user_id, []))

    def grant_stars(self, user_id: str, amount: int, reason: str, idempotency_key: str) -> dict:
        with self._lock:
            idem_key = f"{user_id}:{idempotency_key}"
            existing = self._idempotency_index.get(idem_key)
            if existing is not None:
                return existing

            wallet = self._wallet_by_user.get(user_id)
            if wallet is None:
                wallet = Wallet(money=5000000, stars=20000, medipacks=0)
                self._wallet_by_user[user_id] = wallet
            wallet.stars += amount
            entry = {
                "entryId": str(uuid4()),
                "kind": "grant",
                "currency": "stars",
                "amount": amount,
                "reason": reason,
                "balanceAfter": wallet.stars,
            }
            self._ledger_by_user.setdefault(user_id, []).append(entry)
            self._idempotency_index[idem_key] = {
                "granted": True,
                "amount": amount,
                "wallet": asdict(wallet),
                "entry": entry,
            }
            self._save()
            return self._idempotency_index[idem_key]


ECONOMY_STORE = EconomyStore()
