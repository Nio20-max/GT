# GT Implementation Checklist

This checklist is derived from all `plan/*.md` files and is the execution baseline for production delivery.

## 0. Global Rules

- [ ] Use branch flow: `agent/implement/*` for incremental work and `release/agent-complete` at finalization.
- [ ] Keep `plan/agent_activity.log` updated with timestamped pass/fail events.
- [ ] For each non-trivial code change: tests + run instructions + local verification before commit.
- [ ] Use immutable economy/training/match audit trails.
- [ ] Keep runtime deterministic for core simulation (seeded engine, idempotent schedulers/jobs).

## A. Discovery And Scaffolding

- [ ] Read all `plan/*.md` and extract actionable requirements.
- [ ] Produce `plan/FORMULA_DISCOVERY_REPORT.md` with empirical tests for training formulas.
- [ ] Scaffold backend project (FastAPI + workers + migrations + tests).
- [ ] Scaffold web client (Next.js TypeScript skeleton).
- [ ] Scaffold Android client (Gradle Kotlin app shell with preserved assets pipeline).
- [ ] Write `plan/status/phase-A.md` with outcomes.

Acceptance criteria:
- `plan/IMPLEMENTATION_CHECKLIST.md` exists.
- `plan/FORMULA_DISCOVERY_REPORT.md` exists with experiments, formulas, parameter ranges.
- Base project scaffolding compiles/runs basic checks.

## B. Backend And DB

- [ ] Create PostgreSQL schema + migration system for core domains.
- [ ] Implement monthly partition strategy for heavy time-series tables.
- [ ] Implement API contracts from `plan/04_frontend_backend_api_contract.md`.
- [ ] Add endpoint contract tests.
- [ ] Validate migrations on disposable Postgres.
- [ ] Add backup hooks (base + WAL archive test path under `/mnt/website/GT/backups`).
- [ ] Write `plan/status/phase-B.md`.

Acceptance criteria:
- Migrations pass on disposable DB.
- API tests pass locally.

## C. Match Engine, Training, Bots

- [ ] Implement deterministic match precompute + publish flow.
- [ ] Implement full training tick formula and aging/decay logic.
- [ ] Implement bot personas and population maintenance.
- [ ] Implement transfer/scouting behavior smoke paths.
- [ ] Add telemetry for CPU, memory, DB growth, per-match duration and economy/training health.
- [ ] Write `plan/status/phase-C.md`.

Acceptance criteria:
- Deterministic tests pass.
- Training progression validation tests pass.
- Bot + transfer + scouting smoke tests pass.

## D. Android Rebuild

- [ ] Rebuild Android project (Kotlin/Gradle) with visual parity to APK.
- [ ] Implement core screens and navigation shell.
- [ ] Match networking/auth with backend contracts.
- [ ] Build unsigned APK and validate authentication/navigation against local backend.
- [ ] Write `plan/status/phase-D.md`.

Acceptance criteria:
- Android app builds.
- App authenticates and runs core flows.

## E. Web Client And Admin

- [ ] Implement full web client parity (desktop + mobile responsive).
- [ ] Integrate realtime topics (`chat`, `live-match-events`, `notifications`, `market-updates`).
- [ ] Implement admin controls and replay retrieval.
- [ ] Write `plan/status/phase-E.md`.

Acceptance criteria:
- Web client builds and runs with backend.

## F. Integration Simulation

- [ ] Run fastened deterministic simulation for 3-10 seasons.
- [ ] Record metrics and subsystem validations.
- [ ] Log anomalies into `plan/PROBLEMS.md` with remediations.
- [ ] Apply storage/gameplay fixes and re-run.
- [ ] Produce `plan/SIMULATION_REPORT.md`.
- [ ] Write `plan/status/phase-F.md`.

Acceptance criteria:
- Simulation report includes resources, DB size growth, artifacts, and subsystem checks (training, transfers, scouting, bots, match distributions, economy).

## G. Hardening And Delivery

- [ ] Add operational runbooks under `plan/ops/`.
- [ ] Create `release/agent-complete` branch.
- [ ] Produce release checklist and final artifacts (migration bundle, backend package, unsigned APK).
- [ ] Tag release.
- [ ] Write `plan/status/phase-G.md`.

Acceptance criteria:
- Release branch and artifacts complete.

## Open Clarifications (Need User Decision)

- [ ] Exact training `base_gain` constants by skill class.
- [ ] Exact fatigue model and injury interaction coefficients.
- [ ] Medipack bulk discount tiers.
- [ ] UCL format details (group stage vs direct knockout sequencing specifics).
- [ ] Premium anti-abuse throttle details beyond current caps.
