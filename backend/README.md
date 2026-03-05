# GT Backend

Initial FastAPI scaffold for Goal Tactics.

## Quickstart

1. Create environment and install dependencies:
   - `pip install -e .[dev]`
2. Run API:
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. Run tests:
   - `pytest`

## Disposable Postgres + Migrations

1. Start local Postgres:
   - `docker compose -f docker-compose.pg.yml up -d`
2. Apply SQL migrations:
   - `GT_DB_URL=postgresql://gt:gt@localhost:55432/gt python scripts/apply_migrations.py`
3. Stop local Postgres:
   - `docker compose -f docker-compose.pg.yml down`

## Current Scope

- Health endpoint.
- Deterministic training formula module with tunable constants.
- Initial schema migration file for core domains.
- API envelope + initial contract endpoints (`/api/v1/*`).

## PostgreSQL Repository Mode

- Set `GT_DB_URL` (example: `postgresql://gt:gt@localhost:55432/gt`) to enable PostgreSQL-backed auth/game persistence.
- If `GT_DB_URL` is not set, JSON state files in `GT_STATE_DIR` are used.
- Apply latest migrations before enabling DB-backed mode:
   - `GT_DB_URL=postgresql://gt:gt@localhost:55432/gt python scripts/apply_migrations.py`

## Runtime Ops Endpoints

- `POST /api/v1/admin/scheduler/run-due`
- `GET /api/v1/admin/precompute/artifacts/{fixtureId}`
- `GET /api/v1/admin/settlements`
- `GET /api/v1/admin/metrics/runtime`

## Production Services (systemd)

Service unit templates are provided under `deploy/systemd/` and can be installed via:

- `cd /root/projekte/GT && bash scripts/install_systemd_services.sh`

Installed services:

- `gt-api.service` (FastAPI)
- `gt-scheduler.service` (scheduler worker)
- `gt-bot-worker.service` (bot cycle worker)
- `gt-web.service` (Next.js web)

## Endpoint Verification

- Live API verifier: `scripts/verify_api_endpoints.sh https://gt.nikolai-linschmann.de`
- It validates all HTTP endpoints exposed in OpenAPI and reports pass/fail summary.

## Nginx Domain Config

- Repository template: `deploy/nginx/gt.nikolai-linschmann.de.conf`
- Active server config path on host: `/etc/nginx/sites-available/gt.nikolai-linschmann.de`
