# Production Checklist

Date started: 2026-03-05
Owner: Copilot agent

## 1. Planning And Traceability

- [x] Read all numbered plan documents (`plan/00..15*.md`).
- [x] Maintain implementation checklist and activity log.
- [x] Keep per-phase status files up to date through completion.

## 2. Backend Core

- [x] Implement full API contract surface from `plan/04_frontend_backend_api_contract.md`.
- [ ] Implement deterministic match engine with replay-safe seed rules.
- [x] Implement training tick and aging/decay logic.
- [x] Implement bot personas and lifecycle management.
- [x] Implement transfer/scouting/economy baseline flows.
- [x] Add scheduler entrypoints for lock/precompute/publish/report jobs.

## 3. Database And Storage

- [ ] Expand schema/migrations for all core domains.
- [ ] Validate migrations on disposable Postgres.
- [x] Add retention/partition/archive hooks per storage plan.
- [x] Add backup hooks to `/mnt/website/GT/backups`.

## 4. Web Client

- [x] Build a deployable Next.js client with GT shell and key pages.
- [x] Wire API client + health/bootstrap integration.
- [ ] Validate production build.

## 5. Android Client

- [x] Build reproducible Gradle project.
- [x] Build unsigned APK artifact.
- [x] Place APK in downloadable location.

## 6. Operations And Services

- [x] Add systemd units for API, scheduler, worker, web.
- [x] Add install/start scripts for services.
- [x] Enable and start required services.
- [x] Verify API and service health checks.

## 7. Simulation And Reports

- [x] Run fast multi-season simulation.
- [ ] Generate `plan/SIMULATION_REPORT.md` and update `plan/PROBLEMS.md`.
- [ ] Re-run after fixes until no critical blockers remain.

## 8. Delivery

- [x] Produce release checklist and artifacts.
- [ ] Create release branch and tag.
- [ ] Push all validated changes.
