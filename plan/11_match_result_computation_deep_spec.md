# 11) Match Result Computation Deep Specification

## Purpose
Define how official and on-demand matches are computed, frozen, and presented.

## Goals
1. Competitive integrity through deterministic, server-side simulation.
2. Predictable lock windows and no last-second client exploits.
3. Realistic enough football outcomes with manageable complexity.
4. Fast enough precompute to scale to all leagues/cups daily.

## Match classes
1. League match
- Lock/precompute: `17:00 UTC`
- Playback start: `18:00 UTC`

2. Cup/UCL match
- Lock/precompute: `12:00 UTC`
- Playback start: `13:00 UTC`

3. Friendly
- Lock: `12:00 UTC`
- Start: `13:00 UTC`
- Auto-cancel on cup/UCL conflict for club.

4. Ladder
- User/bot-triggered.
- Immediate result with lighter algorithm.

## Why precompute at lock
1. Removes race conditions from late client actions.
2. Gives stable result artifacts for replay/audit.
3. Enables lightweight playback delivery at kickoff.

## Lock behavior
- Lineup/formation/tactics become frozen for that fixture at lock.
- Post-lock changes are accepted only into queue for next eligible fixture.
- Upgrades/training after lock do not influence frozen fixture.

## Deterministic seed
- `seed = hash(match_id + competition + season_id + seed_version + server_secret)`

## Core engine input model
- Team strength by position groups: GK, DEF, MID, ATT.
- Fitness and injury impacts.
- Tactical fit and mismatch effects.
- Home advantage.
- Active perks and set-piece modifiers.
- Form and morale factors.

## Suggested computation pipeline
1. Preprocess team vectors
- Build normalized attack/defense/control indexes.

2. Chance budget generation
- Compute expected chance counts per side from MID/ATT vs DEF/GK.

3. Chance quality assignment
- For each chance, assign xG-like quality by matchup and tactic state.

4. Event resolution
- Resolve goal/no-goal from deterministic random stream.
- Resolve cards/injuries/substitutions.
- Apply live change commands where allowed.

5. Finalization
- Persist scoreline, event timeline, table effects, player condition effects, finance effects.

## Example formulas (implementation target)
1. Team attack index:
- `ATK = 0.45*ATT + 0.30*MID + 0.10*tactic_attack + 0.10*perk_attack + 0.05*morale`

2. Team defense index:
- `DEF = 0.45*DEF_pos + 0.25*GK + 0.15*tactic_def + 0.10*perk_def + 0.05*fitness`

3. Expected chances:
- `chances = clamp(round(base_chances * (ATK / DEF_opp) * tempo_mod), min_c, max_c)`

4. Chance conversion:
- `p_goal = clamp(base_xg * finishing_mod * keeper_opp_mod * setpiece_mod, 0.02, 0.65)`

## Live substitutions and formation changes
- Enabled in v1.
- Server validates command legality:
  - substitution count limits
  - player availability
  - formation validity
- Command effects apply at next simulation phase boundary.

## Cup/UCL tie handling (to finalize)
- If knockout tie level at full-time:
  - extra-time and penalties logic must be specified in calendar/competition detail file.

## Persistence model
- `match_results`
  - score, winner, tie flags, finalized_at
- `match_event_timeline`
  - minute, event_type, payload, deterministic_index
- `match_precompute_artifacts`
  - frozen_inputs, seed, formula_version, checksum

## Security and anti-tamper
1. No client-submitted stat deltas are trusted.
2. Precompute artifacts signed/checksummed.
3. Pre-kickoff result access restricted.
4. Audit endpoint for admin support with trace ID.

## Failure and recovery
1. If precompute job fails at lock:
- retry with lock-respecting backoff.
- if still failed, circuit-breaker alert and fallback queue.

2. If playback service fails:
- serve result from persisted artifacts directly.

## Goals and how to achieve them
1. Goal: reproducibility
- Achieve with deterministic seeds + formula versioning + artifact storage.

2. Goal: fairness
- Achieve with strict lock enforcement and server-side authoritative calculations.

3. Goal: realism without excessive CPU
- Achieve with phased statistical model, not full per-second physics simulation.

4. Goal: low-latency live experience
- Achieve with precomputed timelines, websocket push, and compact event payloads.

## Acceptance criteria
1. Same inputs and seed always produce same score/event sequence.
2. No post-lock lineup change can alter frozen fixture outcome.
3. League and cup precompute completes within scheduled window.
4. Playback starts exactly at kickoff target time.
