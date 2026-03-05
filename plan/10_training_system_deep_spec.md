# 10) Training System Deep Specification

## Purpose
Define exactly how player training works, why it exists, and how to implement it reliably and fairly.

## Goals
1. Reward long-term planning over short-term spam.
2. Make Talent 10 + perfect planning capable of near-cap progression, but keep cap rare.
3. Keep system legible to users and deterministic for support/debug.
4. Prevent "training account" abuse loops.

## Non-goals
1. Real-time minute-based training updates.
2. Hidden platform-specific advantages.

## Core behavior summary
- Training applies at `00:00 UTC` in a deterministic daily tick.
- Progress uses server-authoritative formulas only.
- Gains slow down after strength `700` and with age.
- Age `30+` introduces daily decay unless anti-age protection is active.
- Max age `34`, max strength `1000`.

## Inputs
- Current player strength `S`
- Talent `T` (1..10)
- Age `A`
- Training style (`conservative`, `balanced`, `aggressive`)
- Team training settings
- Individual training slots (up to 5)
- Training camp modifiers
- Tactics training modifier
- Fatigue and health modifiers
- Anti-age upgrade status

## Locked formulas
1. Initial scouting strength:
- `S0 = clamp(60 + rand(-6, 6) + 2 * (T - 5), 45, 85)`

2. Talent factor:
- `talent_factor = 0.85 + 0.03 * T`

3. Style multipliers:
- conservative: `0.88`
- balanced: `1.00`
- aggressive: `1.14`

4. Age gain multiplier:
- `<=21: 1.16`
- `22-24: 1.06`
- `25-27: 1.00`
- `28-29: 0.90`
- `30: 0.75`
- `31: 0.68`
- `32: 0.60`
- `33: 0.50`
- `34: 0.38`

5. High-strength damping:
- if `S <= 700`: `high_strength_factor = 1`
- if `S > 700`: `high_strength_factor = exp(-(S - 700)/220)`

6. Daily gain:
- `gain = base_gain * style_mult * talent_factor * age_mult * high_strength_factor * camp_mult * indiv_mult * tactic_mult * fatigue_mult`

7. Age 30+ decay without anti-age buff:
- `decay = 0.05 * (A - 29)`

8. Daily update:
- `S_next = min(1000, S + gain - decay)`

## Pricing and progression constraints
1. Individual training tiers (one-time/weekly):
- Tier1: `1000 / 500`
- Tier2: `1500 / 750`
- Tier3: `2000 / 1000`
- Tier4: `2500 / 1250`
- Tier5: `3000 / 1500`

2. Camp repetition:
- Repeats are allowed.
- Repeat cost increases each buy except experience camp.

3. Tactics training:
- Max tactics `150%`.
- Training above `100%` costs `100 stars/day`.
- Gain rate: `2%/day`.

4. Anti-age upgrade:
- 1 season: `10,000 stars`
- 2 seasons: `17,000 stars`
- further seasons: declining incremental curve.

## Why this design
1. Player progression remains meaningful for months, not days.
2. Hard cap remains aspirational and prestige-based.
3. Aging creates strategic roster turnover.
4. Deterministic tick makes support and anti-cheat investigations feasible.

## Data model additions (if missing)
- `player_training_state`
  - current_style
  - fatigue_value
  - anti_age_until_season
  - training_slot_count
- `training_tick_audit`
  - tick_id
  - player_id
  - pre_strength
  - computed_gain
  - computed_decay
  - post_strength
  - formula_version

## Execution sequence at 00:00 UTC
1. Load players eligible for training update.
2. Compute gain/decay deterministically.
3. Apply strength updates in batches with row locks.
4. Insert audit rows.
5. Commit and mark tick checkpoint complete.
6. If failure: rollback and retry idempotently.

## Anti-abuse controls
1. Validate all training purchases against ownership and cooldown.
2. Cap queued training operations per day.
3. Record every star/money deduction in immutable ledger.
4. Reject duplicate requests via idempotency keys.

## Observability
1. Daily median gain by age bucket.
2. % players above 700 and above 900.
3. Tick runtime and retries.
4. Number of skipped/catch-up runs.

## Acceptance criteria
1. Re-running same tick input produces identical output.
2. Strength never exceeds 1000.
3. Age >34 not possible.
4. No player misses training due to scheduler restart (catch-up works).
5. Support can reconstruct any player's day delta from audit logs.
