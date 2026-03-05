# 12) Bot System Deep Specification

## Purpose
Define how bots operate so leagues feel alive while preserving fairness and human-like behavior.

## Goals
1. Keep markets and competitions active even at low human concurrency.
2. Make bots behaviorally plausible and hard to distinguish from humans.
3. Prevent bots from creating obvious economy distortion.
4. Support alliance-aware bot coordination.

## Bot design principles
1. Same rules as humans
- Same cooldowns, same prices, same API validation.
- No hidden stat multipliers.

2. Controlled individuality
- Each bot has persistent profile scores and timezone behavior.

3. Imperfect optimization
- Bots sometimes skip profitable actions to avoid robotic predictability.

## Core bot profile
- `persona_type`: transfer, training, balanced, ladder, youth
- `activeness_score` (0..100)
- `star_buyer_score` (0..100)
- `alliance_loyalty` (0..100)
- `timezone_profile` (mostly Europe)
- `risk_tolerance`
- `social_talkativeness`

Persona mix target:
- transfer/training/balanced/ladder/youth = `25/20/25/15/15`

## Daily star injection
Formula:
- `daily_stars = base(200..1800) + activeness_score*8 + star_buyer_score*12 + league_tier_bonus + noise(+-10%)`

Why:
- Keeps diverse spending power without identical bot behavior.

## Alliance-aware transfer behavior
Internal overbid chance:
- `internal_overbid_chance = max(5%, 40% - 0.35 * loyalty)`

Behavior:
1. Alliance bots share watchlists and preferred targets.
2. High loyalty bots avoid bidding wars against alliance members.
3. Low loyalty bots may still compete occasionally.

## Activity scheduling
- Activeness score maps to session frequency and market checks.
- Timezone profile controls online windows and listing times.
- High-activeness bots can wake for saved-player late bids.

## Auction strategy pipeline
1. Build candidate list from market filters.
2. Score each auction by persona utility:
- short-term team need
- resale value
- age/talent fit
- budget pressure
3. Apply alliance coordination penalties.
4. Apply noise and decide bid/skip.

## Social behavior
- Bots can chat in global, private, group, and alliance channels.
- Message templates vary by persona and context.
- Delays, typos, and occasional silence patterns are injected.

## Ladder and match behavior
- Ladder-focused bots trigger more ladder matches.
- Bots adapt lineups before lock windows.
- Live substitutions are used with bounded frequency.

## Safety and fairness controls
1. Economy caps
- Configure max stars/day injected per bot and per league tier.

2. Pattern detection
- Detect repetitive identical action sequences and rebalance noise.

3. Abuse prevention
- Bot actions are signed by internal service identity.
- Public API never exposes bot flag.

## Data model additions
- `bot_profiles`
- `bot_behavior_state`
- `bot_action_log`
- `bot_alliance_coordination`

## Goals and how to achieve them
1. Goal: realistic competition
- Achieve with persona diversity, timezone scheduling, and imperfect choices.

2. Goal: alliance realism
- Achieve with loyalty-based anti-overbid function and shared targeting.

3. Goal: stability
- Achieve with configurable injection bounds and monitoring metrics.

## Monitoring KPIs
1. Auction participation share by bots vs humans.
2. Price inflation by league tier.
3. Chat activity distribution by channel.
4. Bot win rates in ladder and league.
5. Alliance internal overbid frequency.

## Acceptance criteria
1. Bots follow same API validations as humans.
2. No deterministic repeated sequence across days for same bot.
3. Internal overbid rate statistically follows loyalty curve.
4. Human players cannot reliably classify bots from behavior alone.
