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
