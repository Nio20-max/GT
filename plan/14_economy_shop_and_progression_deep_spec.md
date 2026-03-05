# 14) Economy, Shop, And Progression Deep Specification

## Purpose
Define currencies, sinks/sources, premium grants, ad rewards, and anti-abuse controls.

## Goals
1. Keep economy transparent and server-authoritative.
2. Preserve progression and monetization loops while real payments are disabled.
3. Prevent infinite-farm exploits from reward buttons.
4. Maintain parity across platforms via one server catalog.

## Currencies
1. Money
- Core operational currency for club management.

2. Stars
- Premium currency used for speedups, perks, special actions.

3. Medipacks
- Injury recovery consumable.

## Wallet principles
- Every balance mutation creates immutable ledger entry.
- Balances cannot go negative unless explicitly allowed by rule.
- All grants/spends include trace ID and reason code.

## Launch monetization mode
- Real IAP/ads disabled for launch.
- Existing UI buttons still active.
- Clicking reward/purchase button grants configured amount directly.

## Reward rules
1. Ads reward
- Base: `100 stars/click`
- Daily cap: `15,000 stars`
- Event mode: `200 stars/click`

2. Skill card bundles
- `0.5` for `500 stars`
- `1.25` for `1000 stars`
- `2.5` for `2000 stars`

3. Premium entitlements
- Four tiers active via grant model.
- Daily stars: `500/1000/1500/2000`
- Ad rewards: `110/120/130/140`

4. Group chat creation
- `5,000 stars`

5. Alliance creation
- `20,000 stars`

## Stadium and fan economy
- Unlimited seat expansion with star scaling above old cap.
- Seat pricing currently league-specific.
- Fan/member-related income is amplified relative to prior baseline.

## Transfer market injections
- At season start, inject 24 special youth/talent players.
- Mostly global availability; some lower-league restricted listings.

## Medipack pricing
- Bulk discount behavior required.
- Tier table should be finalized in catalog config.

## Anti-abuse controls
1. Idempotency
- Require idempotency key for every reward grant action.

2. Rate limits
- Per-account and per-IP request ceilings for grant endpoints.

3. Daily caps
- Enforce ad-star cap and premium grant cooldowns.

4. Fraud analytics
- Flag unusual grant cadence, identical repeated intervals, and multi-account patterns.

## Data model
- `wallets`
- `economy_ledger`
- `shop_catalog`
- `shop_events`
- `purchase_grants`
- `premium_entitlements`
- `reward_cap_state`

## Goals and how to achieve them
1. Goal: economy integrity
- Achieve with immutable ledger + strict server-side checks.

2. Goal: smooth temporary no-IAP launch
- Achieve with simulated grants mapped to existing UI offers.

3. Goal: controllable inflation
- Achieve with caps, sinks, and periodic telemetry-based balancing.

## Monitoring KPIs
1. Daily stars minted vs spent.
2. Reward-cap hit rate.
3. Inflation indicators (auction prices by tier).
4. Premium entitlement adoption and retention impact.
5. Medipack consumption by injury duration buckets.

## Acceptance criteria
1. Every currency change is fully auditable.
2. Grant endpoint cannot double-credit via retries.
3. Daily ad cap is enforced exactly.
4. Catalog is platform-independent and consistent.
