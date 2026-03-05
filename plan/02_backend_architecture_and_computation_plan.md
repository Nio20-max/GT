# 2) Server-Side Architecture And Computation Plan

Target stack:
- FastAPI (Python)
- PostgreSQL 15+
- Redis (cache, locks, realtime fanout, queue primitives)
- `systemd` services behind Nginx on `gt.nikolai-linschmann.de`

Locked core decisions:
- League size: 12 clubs
- Official league kickoff: 18:00 UTC
- Official league lock/precompute: 17:00 UTC
- Champions League + Cups kickoff: 13:00 UTC
- Champions League + Cups lock/precompute: 12:00 UTC
- Friendly kickoff slot: 13:00 UTC (daily), auto-cancelled if cup/UCL conflict
- Ladder matches: on-demand, immediate result (no delayed precompute)
- Training gains application: 00:00 UTC
- Daily reports email (ingame mail): 08:00 Europe/London
- Lineup plan size: next 3 matches including friendly
- Post-lock changes: queued for next eligible match
- Starting resources: 5,000,000 money + 20,000 stars
- No ads/IAP payments at launch: buttons exist and grant configured resources

## Core Services
1. API service (`gt-api.service`)
- Auth, gameplay commands, reads, admin controls.
- Server-authoritative all mutations.

2. Simulation service (`gt-sim.service`)
- Official precompute jobs (17:00 and 12:00 UTC windows).
- Training midnight tick.
- Fixture finalization and season rollovers.

3. Bot service (`gt-bot.service`)
- Persona-driven behavior loops.
- Transfer market, training, chat, alliance actions.

4. Realtime service (`gt-rt.service`)
- WebSocket streams: live feed, chat, market, notifications.

5. Worker service (`gt-worker.service`)
- Async deliveries, reports, retries, analytics rollups.

## Database Domains
- Auth: `users`, `sessions`, `auth_providers`
- Club: `clubs`, `club_profiles`, `accomplishments`, `fan_economy`
- Economy: `wallets`, `economy_ledger`, `purchase_grants`, `premium_entitlements`
- Players: `players`, `player_skills`, `player_health`, `player_contracts`, `player_training_state`
- Lineup: `lineups`, `lineup_slots`, `lineup_queue`, `tactics`
- Training: `team_training`, `individual_training_orders`, `training_camps`, `training_tick_audit`
- Scouting: `scouting_jobs`, `scouting_results`, `scout_probability_state`
- Market: `transfer_auctions`, `transfer_bids`, `transfer_watchlist`, `transfer_injections`
- Competitions: `leagues`, `fixtures`, `results`, `tables`, `cup_tournaments`, `ucl_tournaments`
- Ladder: `ladder_runs`, `ladder_matches`, `ladder_stamina`
- Social: `friends`, `friendly_requests`, `chat_channels`, `chat_messages`
- Alliances: `alliances`, `alliance_members`, `alliance_roles`, `alliance_board_threads`, `alliance_cup`
- Bots: `bot_profiles`, `bot_behavior_state`, `bot_schedule_state`, `bot_alliance_loyalty`
- Tasks: `task_catalog`, `user_task_progress`, `user_task_claims`

## Deterministic Model

### Seed strategy
Use deterministic seeds for all competitive outcomes:
- `seed = hash(event_type + event_id + season_id + seed_version + server_secret)`

Deterministic:
- official match outcomes
- training gains
- injuries and recoveries
- scouting result generation

Non-deterministic cosmetic only:
- commentary flavor order
- UI-only animation events

## Match Timing, Locks, and Precompute

### Official league match flow
1. 17:00 UTC: lock official lineup/formation/tactic for tonight's 18:00 league fixture.
2. 17:00 UTC: precompute and persist result payload.
3. 18:00 UTC: publish precomputed timeline as live playback.

### Champions League + Cup flow
1. 12:00 UTC: lock lineup/formation/tactic.
2. 12:00 UTC: precompute and persist result.
3. 13:00 UTC: publish live playback.

### Friendly flow
1. 12:00 UTC: lock friendly lineup.
2. 13:00 UTC: execute friendly.
3. If cup/UCL exists for club at 13:00, friendly auto-cancel (no penalty).

### Ladder flow
- User/bot triggers match explicitly.
- Result computed immediately via lighter ladder algorithm.
- Immediate broadcast of result.

### Lock scope behavior
- Upgrades/training purchases after lock are allowed.
- They do not affect already-locked/precomputed match.
- Attempts to edit locked lineup are queued to next fixture (`lineup_queue`).

## Daily Tick and Report Schedule

### 00:00 UTC training tick
1. Apply training gains.
2. Apply tactics gains/costs.
3. Apply age-related decay where applicable.
4. Resolve injuries/recovery timers.
5. Resolve scout cooldown completions.
6. Apply fixed economy updates.

### 08:00 Europe/London reports
- Deliver ingame emails for training and finances.
- Include friend/friendly request summaries.

## Exact Training and Strength Formulas

### Player initial strength (scouted)
- `S0 = clamp(60 + rand(-6, 6) + 2 * (talent - 5), 45, 85)`

### Talent factor (weaker spread)
- `talent_factor = 0.85 + 0.03 * talent`
- Talent 1 = 0.88, Talent 10 = 1.15

### Training style multipliers
- conservative: `0.88`
- balanced: `1.00`
- aggressive: `1.14`

### Age gain multiplier
- age <= 21: `1.16`
- age 22-24: `1.06`
- age 25-27: `1.00`
- age 28-29: `0.90`
- age 30: `0.75`
- age 31: `0.68`
- age 32: `0.60`
- age 33: `0.50`
- age 34: `0.38`

### High-strength diminishing
- `high_strength_factor = 1` if `S <= 700`
- `high_strength_factor = exp(-(S - 700) / 220)` if `S > 700`

### Daily skill gain
- `gain = base_gain * style_mult * talent_factor * age_mult * high_strength_factor * camp_mult * indiv_mult * tactic_mult * fatigue_mult`

### Strength update
- `S_next = min(1000, S + gain - decay_no_upgrade)`

### Age 30+ decay without upgrade
- if `age >= 30` and no anti-age buff:
  - `decay_no_upgrade = 0.05 * (age - 29)` per day

### Anti-age upgrade (stars)
- 1 season protection: `10,000 stars`
- 2 seasons protection: `17,000 stars`
- additional seasons follow declining incremental pricing curve.

### Retirement
- Max player age: 34

### Progression intent
- Steady growth until 30.
- 1000 cap is technically reachable but only with Talent 10 and near-perfect long-term training.

## Training Content Rules From Goal Tactics
- Individual training slots up to 5 per player.
- Exact cost tiers (one-time/weekly):
  - 1st: 1000 / 500
  - 2nd: 1500 / 750
  - 3rd: 2000 / 1000
  - 4th: 2500 / 1250
  - 5th: 3000 / 1500
- Training camps can repeat.
- Repeats cost more each time, except experience camp.
- Tactics cap: 150%.
- Above 100%, tactic training costs 100 stars/day with 2%/day gain.

## Match Engine (official)
- Inputs:
  - lineup by 4 position groups (GK/DEF/MID/ATT)
  - tactic compatibility
  - fitness, health, morale
  - home bonus and active perks
- Phases:
  1. expected chances
  2. chance quality conversion
  3. event resolution (goals/cards/injuries)
  4. live substitutions/formation changes (enabled in v1)
  5. final stat and economy settlement

## Competitions and Fixture Rules

### Leagues
- 12 clubs per league.
- Daily league fixture at 18:00 UTC.

### Champions League
- 32 clubs.
- Qualification: top 2 from each first league.
- Match slot: 13:00 UTC.

### League cups
- Clubs not in Champions League enter cup.
- Match slot: 13:00 UTC.

### Conflict rules
- No simultaneous multi-competition match for same club.
- If club has cup/UCL fixture, no friendly that day.

## Scouting Rules
- Money scout: 10,000 money, cooldown 12h.
- Special scout: 2,000 stars, cooldown 3h.
- Speedup: 150 stars.
- Include 15-year-old chance mechanic with increasing probability state.
- 17-year-old scouting rule includes talent-10 outcomes.

## Transfer Market Rules
- Full filters, favorites, own-sales views.
- Seasonal injections: 24 special young high-talent players per world.
- Mostly global availability, some restricted to lower leagues.

## Stadium and Economy Rules
- Unlimited seat expansion with star scaling above old cap.
- Seat price remains league-specific (intentional decision).
- Buildings affect training/scouting/fitness/health and money generation.
- Fan/member economy importance increased (shirt/member income).

## Shop, Ads, Premium, and Grants

### Launch payment model
- No real purchases at launch.
- Existing buttons grant configured amount instantly.

### Ads
- Base: 100 stars per click.
- Daily cap: 15,000 stars.
- Event mode supported: 200 stars per click.

### Skill cards shop
- Exact bundles:
  - 0.5 for 500 stars
  - 1.25 for 1000 stars
  - 2.5 for 2000 stars

### Premium (implemented now via entitlement grants)
- Tier set and benefits exactly as listed in `Goal Tactics.md`.
- Daily stars: 500 / 1000 / 1500 / 2000.
- Ad rewards: 110 / 120 / 130 / 140.

## Equipment and Perks
- Perk system enabled in v1.
- Pricing and durations exactly follow `Goal Tactics.md` suggestions.

## Alliances (v1)
- Full alliance system now.
- Creation fee: 20,000 stars.
- Includes alliance chat, alliance board, alliance cup, admin roles.
- Bots participate in alliances.

## Bot System (v1, human-like)

### Persona mix
- transfer/training/balanced/ladder/youth = 25/20/25/15/15

### Core bot profile fields
- `activeness_score` (0..100)
- `star_buyer_score` (0..100)
- `alliance_loyalty` (0..100)
- `timezone_profile` (primarily Europe-focused)
- `persona_type`

### Activity mapping
- sessions/day and market checks scale with `activeness_score`.
- timezone profile controls online windows and transfer listing timing.

### Star injection formula
- `daily_stars = base(200..1800) + activeness_score*8 + star_buyer_score*12 + league_tier_bonus + noise(+-10%)`

### Alliance overbid control
- `internal_overbid_chance = max(5%, 40% - 0.35 * loyalty)`

### Human mimic rules
- chat in all channels (global/private/group/alliance)
- reaction delay and sleep windows
- watchlist late-bid behavior in final 5 minutes
- occasional suboptimal choices

## Chat and Social
- Public chat.
- Private chat.
- Paid group chats (creation cost 5,000 stars).
- Friend list, friendly requests, custom friend series ordering.
- Android parity: show other managers' player strengths.

## Ladder
- On-demand immediate matches.
- Increased prize money.
- No league-based ladder split for now.

## Tasks and Retention
- Daily tasks.
- Weekly tasks.
- Onboarding tasks.
- Rewards in stars and/or money.

## Women world (phase 2)
- Separate women world planned.
- Shared stars wallet across worlds.

## Reliability Safeguards
- Anti-skip training safeguards:
  - idempotent midnight tick checkpoints
  - automatic catch-up if tick missed
  - audit records in `training_tick_audit`
- Ledger-first economy writes for all currencies.
- Idempotency keys for all state-changing actions.

## Suggested `systemd` topology
- `gt-api.service`
- `gt-sim.service`
- `gt-bot.service`
- `gt-worker.service`
- `gt-rt.service`

## Milestones
1. Foundation: auth, clubs, economy ledger, lineup lock model
2. Core sim: official precompute windows, training formulas, scouting
3. Competitions: league/cup/UCL schedulers and conflict rules
4. Market + bots: injections, persona logic, alliance cooperation
5. Social + premium + tasks: chat types, alliances, premium entitlements
6. Hardening: observability, replay audits, anti-abuse and recovery
