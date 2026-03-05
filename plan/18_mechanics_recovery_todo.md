# Mechanics Recovery To-Do (Finalized For Current Scope)

Date: 2026-03-05

This file is updated after implementing all remaining priorities from the previous revision.

## Completed Priorities

### Priority A - Data layer hardening
- Added PostgreSQL repository support with JSON fallback for core state stores.
  - `backend/app/services/pg_repo.py`
  - `backend/app/services/auth_store.py`
  - `backend/app/services/game_store.py`
- Added migration for runtime hardening tables.
  - `backend/migrations/0003_runtime_hardening.sql`
  - Adds `sessions` and `match_settlements`.
- Added DB dependency for runtime repository mode.
  - `backend/pyproject.toml` (`psycopg[binary]`)

### Priority B - Settlement completeness
- Added deterministic settlement recording on fixture publish.
  - `backend/app/services/settlement_store.py`
  - `backend/app/services/runtime_state.py`
- Added settlement visibility endpoint.
  - `GET /api/v1/admin/settlements`

### Priority C - Realtime event bus
- Implemented event bus with cursor-based replay.
  - `backend/app/services/event_bus.py`
- Wired scheduler and gameplay events into bus.
  - `backend/app/workers/scheduler.py`
  - `backend/app/api/routes.py`
- Upgraded websocket to topic subscriptions + replay cursor support.
  - `WS /api/v1/realtime`

### Priority D - Frontend parity completion
- Added typed API helper.
  - `web/app/lib/apiClient.ts`
- Added interactive quick actions in section pages.
  - `web/app/components/section/SectionActions.tsx`
  - Actions for lineup/training/transfer/shop grant.
- Added live realtime feed widget.
  - `web/app/components/RealtimeFeed.tsx`
- Integrated live sections and actions into route pages.
  - `web/app/[section]/page.tsx`
  - `web/app/page.tsx`

### Priority E - Operations and safeguards
- Added rate-limiter service and applied to sensitive endpoints.
  - `backend/app/services/rate_limit.py`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/register`
  - `POST /api/v1/shop/offers/{offerId}/grant`
- Added runtime metrics endpoint.
  - `GET /api/v1/admin/metrics/runtime`
- Added runtime backup/restore scripts.
  - `backend/scripts/ops/backup_runtime_state.sh`
  - `backend/scripts/ops/restore_runtime_state.sh`
- Updated runbook and README.
  - `plan/ops/runbook-backup-restore.md`
  - `backend/README.md`

## Validation Results

- Backend tests: `22 passed`
- Web build: `next build` successful

## New Follow-up Tasks (Non-blocking)

1. Replace JSON fallback paths with strict PostgreSQL-only mode in production.
2. Add Redis-backed distributed event bus and scheduler lock for multi-instance deployments.
3. Add auth/session refresh endpoint backed by `sessions` table rotation.
4. Add richer frontend pages for full lineup editor and transfer filters.
5. Add production dashboards and alert thresholds for `/admin/metrics/runtime` indicators.
