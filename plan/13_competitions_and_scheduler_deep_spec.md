# 13) Competitions And Scheduler Deep Specification

## Purpose
Define exact calendar behavior, fixture conflicts, and compute orchestration for league, cup, UCL, friendly, and ladder.

## Goals
1. One authoritative schedule model with zero ambiguity.
2. No overlapping matches for the same club.
3. Deterministic lock and precompute pipeline.
4. Clear conflict resolution and fallback behavior.

## Time authority
- Use UTC for all gameplay scheduling.
- Use Europe/London only where explicitly stated (reports at 08:00 Europe/London).

## Competition slots
1. League
- lock/precompute: `17:00 UTC`
- kickoff playback: `18:00 UTC`

2. Champions League
- lock/precompute: `12:00 UTC`
- kickoff playback: `13:00 UTC`
- participants: 32 clubs, top 2 from each first league

3. League cups
- lock/precompute: `12:00 UTC`
- kickoff playback: `13:00 UTC`
- participants: clubs not in UCL

4. Friendlies
- lock: `12:00 UTC`
- kickoff: `13:00 UTC`
- auto-cancel if cup/UCL exists for that club/day

5. Ladder
- no fixed kickoff
- on-demand immediate compute

## Conflict rules
1. A club cannot have two matches at same time.
2. UCL participation excludes cup participation for conflicting period.
3. Cup/UCL day suppresses friendly for affected clubs.

## Scheduler jobs
1. `job_lock_precompute_cup_ucl` at 12:00 UTC
2. `job_kickoff_publish_cup_ucl` at 13:00 UTC
3. `job_lock_precompute_league` at 17:00 UTC
4. `job_kickoff_publish_league` at 18:00 UTC
5. `job_training_tick` at 00:00 UTC
6. `job_reports_dispatch` at 08:00 Europe/London

## Why split lock and kickoff
- Allows stable precomputed artifacts before presentation.
- Reduces kickoff CPU spike and improves reliability.

## Lineup queue logic
- If lineup edit arrives after lock:
  - reject for current fixture
  - store as queued draft for next eligible fixture

## Season rollover sequence
1. Final fixture settlement.
2. Table/reward finalization.
3. Transfer injection batch (24 special youth players).
4. Contract/age transitions.
5. New season fixture generation.

## Open implementation details to lock later
1. Cup bracket mechanics (byes vs full knockout path).
2. UCL phase structure (group vs direct knockout).
3. Number of rounds per season and season length.

## Reliability design
1. Each scheduler job idempotent by `(job_type, execution_window)` key.
2. Distributed lock for each job in Redis.
3. Catch-up run on restart for missed windows.
4. Alert when precompute misses SLA.

## Goals and how to achieve them
1. Goal: zero overlap
- Achieve with pre-validation on fixture generation and daily conflict checks.

2. Goal: predictable manager experience
- Achieve with fixed windows and visible countdowns in UI.

3. Goal: operational resilience
- Achieve with idempotent jobs, retries, and checkpoint logs.

## Acceptance criteria
1. No club has overlapping fixtures in same window.
2. Friendly cancel rule works for every cup/UCL conflict case.
3. Precompute artifacts available before kickoff in all normal runs.
4. Missed job recovery reproduces expected state without duplicates.
