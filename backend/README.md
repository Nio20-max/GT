# GT Backend

Initial FastAPI scaffold for Goal Tactics.

## Quickstart

1. Create environment and install dependencies:
   - `pip install -e .[dev]`
2. Run API:
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. Run tests:
   - `pytest`

## Current Scope

- Health endpoint.
- Deterministic training formula module with tunable constants.
- Initial schema migration file for core domains.
