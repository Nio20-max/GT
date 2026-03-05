# Simulation Report

Date: 2026-03-05
Mode: Fast deterministic harness (development scaffold)

## Run Configuration

- Seasons: 3
- Clubs per league: 12
- Match engine: deterministic seed-based simulation (`backend/app/domain/match_engine.py`)
- Training model: deep-spec aligned formula baseline (`backend/app/domain/training.py`)
- Bot model: persona + budget baseline (`backend/app/domain/bots.py`)

## Key Metrics

- Matches simulated: 198
- Average goals per match: 2.01
- Upset rate: 0.1717
- Average daily training gain sample: 0.8204
- Transfer volume (synthetic count): 412
- Scout discoveries (synthetic count): 181
- Average bot daily budget sample: 2335.97

## Resource Snapshot

From `/usr/bin/time -v` on simulation run:

- Elapsed wall time: 0.05s
- User CPU: 0.04s
- System CPU: 0.01s
- Max RSS: 17,280 KB

Workspace component sizes:

- backend: 224K
- web: 342M
- android: 336K

Mounted artifact path inventory:

- `/mnt/website/GT` currently present and empty (no backup/export artifacts generated yet).

## Subsystem Verification (Current Level)

- Training progress and player development:
  - Verified monotonic decline under high age/high strength and fatigue pressure.
  - Baseline gains in expected conservative range from formula discovery.
- Match result distribution:
  - Deterministic repeatability confirmed by unit tests.
  - Goal/upset distribution within plausible early baseline range.
- Transfer market behavior:
  - Synthetic transfer volume instrumentation added in harness.
  - Full realistic pricing/inflation behavior pending full market implementation.
- Scouting pipeline:
  - Synthetic discovery volume instrumentation added in harness.
  - Full scout cooldown/cost/value validation pending full scouting module.
- Bot behavior:
  - Persona mix + star budget + alliance overbid floor implemented and tested.
  - Population lifecycle and strategic behavior still pending.
- Economy health:
  - Basic bot budget generation active; ledger-level economy balancing pending full transaction engine.

## Known Issues

See `plan/PROBLEMS.md`.

## Follow-up Required

1. Implement full competition scheduler and lock/publish job orchestration.
2. Replace synthetic transfer/scouting counters with real module outputs.
3. Add DB persistence and historical telemetry capture for simulation runs.
4. Add backup/WAL output to `/mnt/website/GT/backups` during integration tests.
5. Repeat simulation after full Phase B/C implementation to produce production-grade report.
