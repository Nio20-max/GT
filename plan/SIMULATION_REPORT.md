# Simulation Report

Date: 2026-03-05
Mode: Fast deterministic harness (expanded run)

## Run Configuration

- Seasons: 30
- Leagues: 8
- Clubs per league: 12
- Total league matches simulated: 15,840
- Match engine: deterministic seed-based simulation (`backend/app/domain/match_engine.py`)
- Training model: deep-spec aligned formula baseline (`backend/app/domain/training.py`)
- Bot model: persona + budget baseline (`backend/app/domain/bots.py`)

Command used:

- `/usr/bin/time -v /root/projekte/GT/.venv/bin/python backend/scripts/simulate_fast_mode.py --seasons 30 --leagues 8 --clubs-per-league 12 --output plan/simulations/sim_30seasons_8leagues.json`

## Key Metrics

- Matches simulated: 15,840
- Average goals per match: 2.201
- Upset rate: 0.2064
- Average training gain sample: 0.8000
- Transfer volume (synthetic count): 31,468
- Scout discoveries (synthetic count): 15,756
- Average bot daily budget sample: 2,377.60

## Resource Snapshot

From `/usr/bin/time -v` on expanded run:

- Elapsed wall time: 0.58s
- User CPU: 0.49s
- System CPU: 0.02s
- Max RSS: 18,432 KB

## Seasonal Stability Review

- Per-season avg goals range: 2.038 to 2.366
- Per-season upset-rate range: 0.1875 to 0.2348
- Transfer and scouting volumes remained stable across seasons with expected random variation.

## Assessment

- Match output is plausible for an early deterministic baseline (goal average near low-mid real football range).
- Upset rate is somewhat volatile in late seasons but remains within acceptable baseline for simulation variety.
- Training progression remains conservative as requested.
- Bot star budgets are high enough to keep market movement active in the synthetic model.

## Changes Considered After Analysis

- No immediate formula change applied from this run.
- Recommended next change if realism tightening is desired:
  - Slightly lower upset volatility by increasing quality delta influence in match chance allocation.
  - Introduce per-league calibration profiles to keep goals in 2.1-2.4 target corridor.

## Artifacts

- Raw stats JSON: `plan/simulations/sim_30seasons_8leagues.json`
- Problems list: `plan/PROBLEMS.md`

## Remaining Gaps Before Final Gameplay Claim

1. Replace synthetic transfer/scouting counters with persistence-backed modules.
2. Persist match events and artifacts to DB + archive tiers.
3. Execute equivalent 30-season run against fully persistent stack and compare drift.
