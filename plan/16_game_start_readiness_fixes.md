# Game Start Readiness Fixes (2026-03-05)

This file captures what was still missing for users to start playing and what was fixed in this pass.

## Missing Items Identified

1. Backend state was volatile across service restarts (accounts, sessions, fixtures, contract writes).
2. New accounts had no guaranteed club and no starter squad, so users could not begin core management actions.
3. `/club` endpoint returned static mock data instead of authenticated user-specific state.
4. `/squad` endpoint was contract-mock only, so no actual starter roster was available.
5. League progression visibility was weak for users (no real table/results endpoints tied to runtime results).
6. Endpoint smoke script did not authenticate protected gameplay endpoints.

## Fixes Applied

1. Persistent auth store implemented and enabled.
   - `backend/app/services/auth_store.py`
   - Persists users and tokens to `GT_STATE_DIR` (`auth_state.json`), including expiry cleanup.
2. Persistent runtime scheduler state implemented and enabled.
   - `backend/app/services/runtime_state.py`
   - Persists season + fixtures/results/status to `runtime_state.json`.
3. Persistent gameplay onboarding state implemented.
   - `backend/app/services/game_store.py`
   - Auto-creates club + 16-player starter squad for each registered manager.
4. Shared atomic JSON persistence utility added.
   - `backend/app/services/persistent_json.py`
5. Authenticated user-specific core gameplay endpoints implemented.
   - `backend/app/api/routes.py`
   - Real handlers: `/club`, `/squad`, `/league/current`, `/league/table`, `/league/results`.
6. Registration/profile flow now ensures playable game state exists.
   - `backend/app/api/routes.py`
7. Contract endpoint state persistence added for non-core modules.
   - `backend/app/api/routes.py` (`ContractState` persisted to `contract_state.json`).
8. Verification script updated for protected endpoints.
   - `scripts/verify_api_endpoints.sh`
   - Adds auth flow and bearer token handling for `/club` and `/squad` checks.

## Verification

1. Backend tests passed:
   - `tests/test_auth_flow.py`
   - `tests/test_api_surface.py`
   - `tests/test_api_contract_basics.py`
2. Web build passed:
   - `web: npm run build`
3. Runtime smoke checks passed on running services:
   - register: `201`
   - login: token issued
   - `/club` (authorized): `200`
   - `/squad` (authorized): `200`
   - `/admin/ticks/run`: `200`
   - `/league/table`: `200`
4. Restart persistence check passed:
   - same `clubId` before/after API restart, starter squad count preserved (`16`).

## Remaining Items

Items that cannot be fully completed in this pass are tracked in:
- `plan/17_game_start_blocked_items.md`
