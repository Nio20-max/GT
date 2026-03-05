# Release Checklist

## Service Health

- [x] `gt-api.service` active
- [x] `gt-scheduler.service` active
- [x] `gt-bot-worker.service` active
- [x] `gt-web.service` active
- [x] API health responds (`/health`)
- [x] Bootstrap endpoint responds (`/api/v1/bootstrap`)

## Artifacts

- [x] Debug APK: `/mnt/website/GT/artifacts/GoalTactics-0.1.0-debug.apk`
- [x] Unsigned APK: `/mnt/website/GT/artifacts/GoalTactics-0.1.0-unsigned.apk`
- [x] Simulation report: `plan/SIMULATION_REPORT.md`
- [x] Problems log: `plan/PROBLEMS.md`

## Validation

- [x] Backend tests pass (`16 passed`)
- [x] Web build passes
- [x] Android debug build passes
- [x] Android release build passes

## Pending Before Production Claim

- [ ] Full 1:1 feature parity for all Android and web gameplay flows.
- [ ] Fully implemented backend business logic for every contract endpoint.
- [ ] Comprehensive persistence and migration coverage for all domains.
- [ ] Full integration simulation with complete game stack behavior.
