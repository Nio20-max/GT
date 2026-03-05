# Phase B Status

## Scope

- Database schema/migrations.
- API contract implementation.
- Disposable Postgres validation.

## Current State

- Completed: initial migration `backend/migrations/0001_core_schema.sql` for core domains (`users`, `clubs`, `players`, `matches`, `training_logs`, `economy_transactions`).
- Completed: partitioned table baseline for `training_logs` and `economy_transactions`.
- Completed: API envelope and first contract endpoints:
  - `POST /api/v1/auth/login`
  - `GET /api/v1/bootstrap`
  - `GET /api/v1/club`
  - `POST /api/v1/training/preview`
  - `GET /api/v1/admin/scheduler/windows`
- Completed: disposable Postgres migration run via `docker compose` + migration script.

## Verification

- Backend tests: `9 passed` (`/root/projekte/GT/.venv/bin/python -m pytest`).
- Migration apply run against local Postgres succeeded.
- Schema smoke check confirmed six core tables and partitioned status.

## Remaining For Full Phase B

1. Add remaining contract endpoints from `plan/04_frontend_backend_api_contract.md`.
2. Expand migrations for all domains (lineups, tactics, scouting, transfer market, alliances, chat, tasks, telemetry).
3. Add WAL archival and backup hooks under `/mnt/website/GT/backups` (test-safe paths).
4. Add endpoint-level contract tests for all implemented endpoints.
