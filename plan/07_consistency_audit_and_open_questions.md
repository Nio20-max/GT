# 7) Consistency Audit And Open Questions

Scope reviewed:
- `plan/00_setup_overview.md`
- `plan/01_apk_overview_and_ui_analysis.md`
- `plan/02_backend_architecture_and_computation_plan.md`
- `plan/03_app_ui_rebuild_spec.md`
- `plan/04_frontend_backend_api_contract.md`
- `plan/05_web_client_plan.md`
- `plan/06_current_server_inventory.md`

## Resolved inconsistencies
1. Daily report timezone mismatch
- Issue: backend plan had `08:00 UTC` while overview/API used `08:00 Europe/London`.
- Resolution: backend plan aligned to `08:00 Europe/London`.

2. App feature module list ambiguity
- Issue: Champions League/Cups/Alliances/Tasks/Premium appeared nested under Shop due indentation.
- Resolution: normalized as top-level feature fragments list entries.

## Remaining consistency checks (no hard conflict, but needs explicit lock)
1. Goal Tactics naming
- Files mostly use GT shorthand.
- Confirm whether docs should use only `Goal Tactics` branding until rename decision is finalized.
- Answer from user: The name is Goal Tactics. The shorthand for that is GT. Mostly use Goal Tactics in the app. 

2. Timezone policy wording
- Runtime uses fixed UTC for match/tick windows and Europe/London only for reports.
- Recommend adding one authoritative sentence in every operational doc: "All game logic uses UTC unless explicitly labeled otherwise."
- Answer from user: Exactly that should be used

3. Mobile vs web parity wording
- Android is implementation focus now, but some files still say full parity across all clients.
- Recommend splitting wording into:
  - server parity contract (same game logic)
  - client rollout priority (Android first)

4. Precompute semantics
- "Precompute and persist at lock" is defined, but replay privacy rules are not:
  - who can query precomputed result before kickoff?
    - The user shouldn't be able to see them and they shouldn't be computated in the league table. They should be presaved in an extra column in the database and only moved over when the game begins. 
  - should DB row be encrypted or access-restricted until kickoff?

## Open questions for implementation teams

### A. Training domain
1. Base gain constants
- Formula structure is set, but `base_gain` per skill/age bucket is not numerically locked.
2. Fatigue model
- How exactly fatigue is computed daily and per match is still open.
3. Injury interaction with aggressive training
- Is injury risk additive or multiplicative by training style?

### B. Match computation
1. Live substitution authority
- Allowed substitution count and windows are not yet explicit.
- Answer from user: There is no substitution by the user allowed. 
2. Match event granularity
- Required event cadence for live ticker (minute-by-minute vs event bursts).
- Answer from user: Minute by minute. 
3. Draw/OT/penalty handling
- Cup/UCL knockout tie resolution rules not locked.
- Answer from user: It should go directly to penalty shootout. For that the penalty strength for the player should be used. 

### C. Bot system
1. Population ratio
- Number of bots vs humans per league/world is open.
- Answer from user: It should be so that all leagues are filled with enough teams. If a new user comes along a bot account in a lower league gets deleted. 
2. Bot identity masking
- Exact UI-level anti-fingerprint rules (naming patterns, login rhythm variance) are open.
- Answer from user: Random user and club names for the bots, that drain from a preset list that is long enough, a list from the internet with thousands of names would be best. 
3. Bot economy guardrails
- Max daily stars injected per league tier not capped yet.

### D. Competitions and calendar
1. Cup structure details
- Round structure for non-UCL clubs (group/knockout/byes) is open.
- Answer from user: Directly knockout. 
2. Season length and rollover date
- Number of matchdays and exact rollover sequence are not fixed.
- Answer from user: There are 12 teams per league, so it should be 22 matches per season. 

### E. Economy and monetization
1. Medipack bulk discount curve
- Requirement exists, exact tier table not yet specified.
2. Premium grant abuse controls
- Since purchase buttons grant instantly for now, anti-farm policy needs hard limits and cooldowns.
- Answer from user: Include them
3. Ad event trigger policy
- Event frequency and duration are not yet defined.
- Answer from user: Once at the beginning of every season and then randomly once in the middle of the season. 

### F. Operations
1. Single-host readiness
- Existing host is underpowered for production; migration timing and cutover plan are open.
2. Observability
- SLOs and alert thresholds are not yet documented.

## Recommended next lock order
1. Training constants and fatigue/injury equations
2. Match event/knockout resolution rules
3. Bot population and injection caps
4. Cup bracket and season calendar specifics
5. Abuse controls for simulated monetization
