# Goal Tactics — Implementation Checklist

> **Stack**: Python/FastAPI · PostgreSQL 15+ · Redis 7+ · Kotlin Android · Next.js App Router + TypeScript
> **Domain**: `gt.nikolai-linschmann.de` · **League size**: 12 clubs · **Season**: 22 match-days
> **Starting resources**: 5,000,000 money + 20,000 stars
> **Schedule** (all UTC unless noted): League 18:00 | Cup/UCL 13:00 | Training tick 00:00 | Reports 08:00 Europe/London

---

## Phase A — Discovery & Scaffolding

### A.1 Read & internalise plan documents
- [ ] Read `00_setup_overview.md` — locked decisions, schedule, deliverables
- [ ] Read `01_apk_overview_and_ui_analysis.md` — APK structure, UI architecture, design tokens
- [ ] Read `02_backend_architecture_and_computation_plan.md` — services, DB domains, formulas, milestones
- [ ] Read `03_app_ui_rebuild_spec.md` — shell layout, feature fragments, XML/Kotlin examples
- [ ] Read `04_frontend_backend_api_contract.md` — full API surface, envelopes, WebSocket events
- [ ] Read `05_web_client_plan.md` — Next.js architecture, responsive rules, deployment
- [ ] Read `06_current_server_inventory.md` — host specs, installed software, capacity risks
- [ ] Read `07_consistency_audit_and_open_questions.md` — resolved issues, open questions, user answers
- [ ] Read `10_training_system_deep_spec.md` — formulas, pricing tiers, tick sequence, anti-abuse
- [ ] Read `11_match_result_computation_deep_spec.md` — engine pipeline, seed strategy, persistence
- [ ] Read `12_bot_system_deep_spec.md` — personas, star injection, alliance behaviour, KPIs
- [ ] Read `13_competitions_and_scheduler_deep_spec.md` — slots, conflict rules, scheduler jobs, season rollover
- [ ] Read `14_economy_shop_and_progression_deep_spec.md` — currencies, rewards, caps, anti-abuse
- [ ] Read `15_storage_and_db_architecture.md` — hot/warm/cold tiers, partitioning, backup runbook

### A.2 Formula & constant discovery
- [ ] Catalogue all training formulas (initial strength, talent factor, style mults, age mults, high-strength damping, daily gain, decay)
- [ ] Catalogue match-engine formulas (ATK/DEF indexes, expected chances, chance conversion p_goal)
- [ ] Catalogue bot formulas (daily star injection, internal overbid chance)
- [ ] Catalogue economy constants (ad reward 100★/click, daily cap 15,000★, skill-card bundles, premium tiers)
- [ ] Catalogue scouting constants (money scout 10,000₵/12 h, special scout 2,000★/3 h, speedup 150★)
- [ ] Catalogue individual training tier costs (Tier 1–5 one-time/weekly)
- [ ] Catalogue anti-age upgrade pricing (1 season 10,000★, 2 seasons 17,000★, declining curve)
- [ ] Catalogue tactics training rules (cap 150%, above 100% costs 100★/day, +2%/day gain)
- [ ] Confirm `base_gain` per skill/age bucket (open question — lock value)
- [ ] Confirm fatigue model details (open question — lock formula)
- [ ] Confirm medipack bulk-discount tier table (open question — lock values)

### A.3 Project scaffolding
- [ ] Create monorepo root with `backend/`, `android/`, `web/`, `infra/`, `docs/` directories
- [ ] Initialise Python project (`backend/`) — `pyproject.toml`, FastAPI, Uvicorn, Alembic, SQLAlchemy, `pytest`
- [ ] Initialise Android project (`android/`) — Kotlin, Gradle, min SDK, landscape default, Jetpack libs
- [ ] Initialise Next.js project (`web/`) — App Router, TypeScript, Tailwind, ESLint
- [ ] Create shared design-token file with APK colours (`#1D2B03` bg, `#AFD50C` accent, `#FFFFFF` text, `#FFFF00` highlight)
- [ ] Set up CI pipeline (lint → build → test) for each sub-project
- [ ] Set up `.env.example` with all required environment variables
- [ ] Configure pre-commit hooks (black/ruff, ktlint, eslint/prettier)

---

## Phase B — Backend + Database

### B.1 PostgreSQL schema & migrations
- [ ] Create Alembic migration environment and `alembic.ini`
- [ ] **Auth domain**: `users`, `sessions`, `auth_providers`
- [ ] **Club domain**: `clubs`, `club_profiles`, `accomplishments`, `fan_economy`
- [ ] **Economy domain**: `wallets`, `economy_ledger`, `purchase_grants`, `premium_entitlements`, `reward_cap_state`
- [ ] **Player domain**: `players`, `player_skills`, `player_health`, `player_contracts`, `player_training_state`
- [ ] **Lineup domain**: `lineups`, `lineup_slots`, `lineup_queue`, `tactics`
- [ ] **Training domain**: `team_training`, `individual_training_orders`, `training_camps`, `training_tick_audit`
- [ ] **Scouting domain**: `scouting_jobs`, `scouting_results`, `scout_probability_state`
- [ ] **Market domain**: `transfer_auctions`, `transfer_bids`, `transfer_watchlist`, `transfer_injections`
- [ ] **Competition domain**: `leagues`, `fixtures`, `results`, `tables`, `cup_tournaments`, `ucl_tournaments`
- [ ] **Ladder domain**: `ladder_runs`, `ladder_matches`, `ladder_stamina`
- [ ] **Social domain**: `friends`, `friendly_requests`, `chat_channels`, `chat_messages`
- [ ] **Alliance domain**: `alliances`, `alliance_members`, `alliance_roles`, `alliance_board_threads`, `alliance_cup`
- [ ] **Bot domain**: `bot_profiles`, `bot_behavior_state`, `bot_action_log`, `bot_alliance_coordination`
- [ ] **Task domain**: `task_catalog`, `user_task_progress`, `user_task_claims`
- [ ] **Shop domain**: `shop_catalog`, `shop_events`
- [ ] **Match artifacts**: `match_results`, `match_event_timeline`, `match_precompute_artifacts`
- [ ] Add monthly range partitions on `created_at` for `match_results`, `match_event_timeline`, `training_tick_audit`, `economy_ledger`
- [ ] Add artifact columns (`artifact_path`, `artifact_hash`) for large replay blobs
- [ ] Run and verify all migrations against a clean database

### B.2 Core backend services & auth
- [ ] Implement JWT auth with refresh tokens (`POST /auth/register`, `/login`, `/refresh`, `/logout`)
- [ ] Implement `Idempotency-Key` header middleware for all write endpoints
- [ ] Implement `GET /bootstrap` — user + club snapshot + unread counts + menu badges
- [ ] Implement `GET /hud/resources` — stars, money, medipacks, active cooldowns
- [ ] Implement `GET /runtime/calendar` — next lock/kickoff times per competition
- [ ] Implement `GET /runtime/locks` — current lock status
- [ ] Implement `GET /notifications/unread-count`
- [ ] Implement standard response envelopes (`{ ok, data, traceId }` / `{ ok, error: { code, message }, traceId }`)
- [ ] Set up Redis connection pool for cache, locks, and queue primitives
- [ ] Create deterministic seed utility: `seed = hash(event_type + event_id + season_id + seed_version + server_secret)`

### B.3 Club & profile endpoints
- [ ] `GET /club` — club details
- [ ] `PATCH /club/name` — rename club
- [ ] `GET /club/accomplishments`
- [ ] `GET /club/fans-members`
- [ ] `GET /club/season-history`
- [ ] `GET /club/all-time-tables`
- [ ] `GET /me/profile`, `PATCH /me/profile`
- [ ] `GET /me/settings`, `PATCH /me/settings`

### B.4 Economy & finance endpoints
- [ ] `GET /finances/summary`
- [ ] `GET /finances/history?days=30`
- [ ] `GET /finances/ledger?cursor=…`
- [ ] `GET /finances/stars-history?days=30`
- [ ] Implement immutable ledger writes for every balance mutation with trace ID and reason code
- [ ] Enforce balance-cannot-go-negative rule

### B.5 Stadium & building endpoints
- [ ] `GET /stadium`
- [ ] `GET /stadium/buildings`
- [ ] `POST /stadium/buildings/{buildingId}/upgrade`
- [ ] `POST /stadium/buildings/{buildingId}/speedup`
- [ ] `POST /stadium/buildings/{buildingId}/deconstruct`
- [ ] `GET /stadium/seats/pricing`
- [ ] Implement unlimited seat expansion with star-scaling above old cap
- [ ] Implement building effects on training/scouting/fitness/health/money generation

### B.6 Squad & player endpoints
- [ ] `GET /squad`
- [ ] `GET /players/{playerId}`
- [ ] `POST /players/{playerId}/skill-cards/apply`
- [ ] `POST /players/{playerId}/upgrade`
- [ ] `POST /players/{playerId}/rename`
- [ ] `POST /players/{playerId}/change-origin`
- [ ] `POST /players/{playerId}/heal`
- [ ] `POST /players/{playerId}/sell`
- [ ] `GET /players/{playerId}/anti-age-upgrade-options`
- [ ] `POST /players/{playerId}/anti-age-upgrade`

### B.7 Lineup & tactics endpoints
- [ ] `GET /lineup/current`
- [ ] `PUT /lineup/current`
- [ ] `GET /lineup/upcoming?limit=3` — next 3 matches including friendly
- [ ] `PUT /lineup/upcoming/{fixtureId}`
- [ ] `GET /tactics`
- [ ] `PUT /tactics`
- [ ] `GET /lineup/lock-status/{fixtureId}`
- [ ] `POST /lineup/queue-change/{fixtureId}` — post-lock changes queued to next eligible match
- [ ] Implement lock behaviour: freeze lineup/formation/tactics at lock time; reject edits, queue to next fixture

### B.8 Training endpoints
- [ ] `GET /training/overview`
- [ ] `POST /training/team`
- [ ] `POST /training/individual`
- [ ] `POST /training/camps/{campId}/book`
- [ ] `POST /training/tactics/{tacticId}/train`
- [ ] `GET /training/progress?playerId=…`
- [ ] `GET /training/formulas` — expose read-only formula reference
- [ ] `GET /training/individual-tiers` — cost table (Tier 1–5)
- [ ] `GET /training/camps/{campId}/repeat-cost`
- [ ] Implement individual training slot purchase validation (up to 5 slots per player)

### B.9 Scouting endpoints
- [ ] `GET /scouting/overview`
- [ ] `POST /scouting/instruct` — money scout (10,000₵, 12 h cooldown)
- [ ] `POST /scouting/instruct-special` — star scout (2,000★, 3 h cooldown)
- [ ] `POST /scouting/speedup` — (150★)
- [ ] `GET /scouting/results`
- [ ] `POST /scouting/results/{resultId}/sign`
- [ ] `GET /scouting/probability-state`
- [ ] Implement 15-year-old chance mechanic with increasing probability state
- [ ] Implement 17-year-old talent-10 outcome rules

### B.10 Transfer market endpoints
- [ ] `GET /transfer/auctions?filters=…`
- [ ] `GET /transfer/auctions/{auctionId}`
- [ ] `POST /transfer/auctions/{auctionId}/bid`
- [ ] `POST /transfer/auctions/{auctionId}/favorite`
- [ ] `DELETE /transfer/auctions/{auctionId}/favorite`
- [ ] `GET /transfer/my-sales`
- [ ] `GET /transfer/my-bids`
- [ ] `GET /transfer/favorites`
- [ ] `GET /transfer/seasonal-injections`
- [ ] Implement seasonal injection: 24 special youth high-talent players per world at season start

### B.11 Sponsors & email endpoints
- [ ] `GET /sponsors/offers`
- [ ] `POST /sponsors/{offerId}/accept`
- [ ] `GET /emails` — in-game mail list
- [ ] `GET /emails/{emailId}`
- [ ] `POST /emails/{emailId}/read`
- [ ] `DELETE /emails/{emailId}`

### B.12 Competition endpoints (league, UCL, cups)
- [ ] `GET /league/current`
- [ ] `GET /league/table`
- [ ] `GET /league/fixtures`
- [ ] `GET /league/results`
- [ ] `GET /league/topscorers`
- [ ] `GET /matches/{matchId}`
- [ ] `GET /matches/{matchId}/live`
- [ ] `GET /matches/{matchId}/report`
- [ ] `GET /ucl/current`
- [ ] `GET /ucl/fixtures`
- [ ] `GET /ucl/table`
- [ ] `GET /cups/current`
- [ ] `GET /cups/fixtures`
- [ ] `GET /cups/bracket`

### B.13 Ladder endpoints
- [ ] `GET /ladder/overview`
- [ ] `GET /ladder/fixtures`
- [ ] `POST /ladder/matches/{matchId}/start` — on-demand immediate result
- [ ] `POST /ladder/stamina/refill`
- [ ] `GET /ladder/ranking`

### B.14 Social & chat endpoints
- [ ] `GET /friends`
- [ ] `POST /friends/search`
- [ ] `POST /friends/requests/{managerId}`
- [ ] `POST /friends/requests/{requestId}/accept`
- [ ] `POST /friends/requests/{requestId}/decline`
- [ ] `DELETE /friends/{friendId}`
- [ ] `POST /friendlies/invite`
- [ ] `GET /friendlies/requests`
- [ ] `GET /friends/series`, `PUT /friends/series`
- [ ] `GET /clubs/{clubId}/public-squad`
- [ ] `GET /chat/channels`
- [ ] `GET /chat/channels/{channelId}/messages?cursor=…`
- [ ] `POST /chat/channels/{channelId}/messages`
- [ ] `POST /chat/groups` — creation cost 5,000★
- [ ] `GET /chat/private/{managerId}`

### B.15 Alliance endpoints
- [ ] `POST /alliances` — creation fee 20,000★
- [ ] `GET /alliances/{allianceId}`
- [ ] `POST /alliances/{allianceId}/join-request`
- [ ] `POST /alliances/{allianceId}/members/{memberId}/approve`
- [ ] `POST /alliances/{allianceId}/members/{memberId}/kick`
- [ ] `GET /alliances/{allianceId}/chat`
- [ ] `GET /alliances/{allianceId}/board`
- [ ] `POST /alliances/{allianceId}/board/threads`
- [ ] `GET /alliances/{allianceId}/cup`
- [ ] `POST /alliances/{allianceId}/cup/lineup`

### B.16 Shop, rewards & premium endpoints
- [ ] `GET /shop/catalog`
- [ ] `POST /shop/offers/{offerId}/grant` — simulated purchase (no real IAP at launch)
- [ ] `GET /shop/grants/history`
- [ ] `GET /shop/events`
- [ ] `GET /shop/premium/tiers` — daily stars 500/1000/1500/2000, ad rewards 110/120/130/140
- [ ] `POST /shop/premium/{tierId}/grant`
- [ ] Implement ad reward: 100★/click, daily cap 15,000★, event mode 200★/click
- [ ] Implement skill-card bundles: 0.5 for 500★ | 1.25 for 1,000★ | 2.5 for 2,000★
- [ ] Enforce per-account and per-IP rate limits on grant endpoints
- [ ] Enforce daily ad-star cap and premium grant cooldowns
- [ ] Implement fraud analytics flags for unusual grant cadence

### B.17 Equipment & cosmetics endpoints
- [ ] `GET /equipment/catalog`
- [ ] `POST /equipment/shirts/{id}/buy`
- [ ] `POST /equipment/emblems/{id}/buy`
- [ ] `POST /equipment/perks/{id}/activate`
- [ ] `GET /equipment/perks/pricing`

### B.18 Task endpoints
- [ ] `GET /tasks/onboarding`
- [ ] `GET /tasks/daily`
- [ ] `GET /tasks/weekly`
- [ ] `POST /tasks/{taskId}/claim`

### B.19 WebSocket / realtime service
- [ ] `WS /realtime` — multiplexed topics
- [ ] Implement event: `hud.updated`
- [ ] Implement event: `chat.message.created`
- [ ] Implement event: `transfer.auction.updated`
- [ ] Implement event: `match.live.event`
- [ ] Implement event: `notification.created`
- [ ] Implement event: `fixture.locked`
- [ ] Implement event: `match.precomputed`
- [ ] Implement event: `task.completed`
- [ ] Implement event: `alliance.updated`

### B.20 Admin / ops endpoints
- [ ] `POST /admin/ticks/run`
- [ ] `POST /admin/bots/run-cycle`
- [ ] `POST /admin/seasons/rollover`
- [ ] `GET /admin/health/deep`
- [ ] `POST /admin/precompute/run?competition=league|cup|ucl`
- [ ] `POST /admin/training-tick/run`
- [ ] `POST /admin/training-tick/catchup`
- [ ] `POST /admin/transfer/injections/run`

---

## Phase C — Match Engine, Training Tick & Bots

### C.1 Deterministic match engine
- [ ] Implement team vector preprocessing (normalised ATK/DEF/control indexes)
  - `ATK = 0.45*ATT + 0.30*MID + 0.10*tactic_attack + 0.10*perk_attack + 0.05*morale`
  - `DEF = 0.45*DEF_pos + 0.25*GK + 0.15*tactic_def + 0.10*perk_def + 0.05*fitness`
- [ ] Implement chance budget generation
  - `chances = clamp(round(base_chances * (ATK / DEF_opp) * tempo_mod), min_c, max_c)`
- [ ] Implement chance quality / xG conversion
  - `p_goal = clamp(base_xg * finishing_mod * keeper_opp_mod * setpiece_mod, 0.02, 0.65)`
- [ ] Implement event resolution (goals, cards, injuries) from deterministic random stream
- [ ] Implement minute-by-minute event timeline generation
- [ ] Implement penalty shootout for cup/UCL knockouts (use player penalty strength)
- [ ] Implement home-advantage modifier
- [ ] Implement perk and set-piece modifiers
- [ ] Implement form and morale factors
- [ ] Implement final stat and economy settlement post-match
- [ ] Implement precompute artifact persistence (`match_precompute_artifacts`: frozen inputs, seed, formula version, checksum)
- [ ] Implement result privacy: precomputed results stored in separate column, only moved to live on kickoff
- [ ] Implement lighter ladder match algorithm (immediate result, no precompute)
- [ ] Write determinism tests: same inputs + seed → identical score/events

### C.2 Scheduler jobs
- [ ] `job_lock_precompute_cup_ucl` — runs at 12:00 UTC
- [ ] `job_kickoff_publish_cup_ucl` — runs at 13:00 UTC
- [ ] `job_lock_precompute_league` — runs at 17:00 UTC
- [ ] `job_kickoff_publish_league` — runs at 18:00 UTC
- [ ] `job_training_tick` — runs at 00:00 UTC
- [ ] `job_reports_dispatch` — runs at 08:00 Europe/London (intentionally not UTC; follows local time so reports arrive at a consistent wall-clock hour for the primary user base, shifts ±1 h with DST)
- [ ] Implement friendly auto-cancel when cup/UCL exists for that club/day
- [ ] Implement conflict validation: no club has two matches at same time
- [ ] Make every job idempotent by `(job_type, execution_window)` key
- [ ] Implement Redis distributed lock per job
- [ ] Implement catch-up run on service restart for missed windows
- [ ] Implement SLA alerting when precompute misses deadline

### C.3 Training tick (00:00 UTC)
- [ ] Load all players eligible for training update
- [ ] Compute `talent_factor = 0.85 + 0.03 * T`
- [ ] Apply style multiplier (conservative `0.88`, balanced `1.00`, aggressive `1.14`)
- [ ] Apply age gain multiplier (≤21: `1.16` → 34: `0.38`)
- [ ] Apply high-strength damping (`exp(-(S-700)/220)` when S > 700)
- [ ] Compute `gain = base_gain * style_mult * talent_factor * age_mult * high_strength_factor * camp_mult * indiv_mult * tactic_mult * fatigue_mult`
- [ ] Compute age 30+ decay: `decay = 0.05 * (A - 29)` (skip if anti-age active)
- [ ] Apply `S_next = min(1000, S + gain - decay)`
- [ ] Resolve injury/recovery timers
- [ ] Resolve scout cooldown completions
- [ ] Apply fixed economy updates
- [ ] Batch-update with row locks, insert `training_tick_audit` rows
- [ ] Commit and mark tick checkpoint; rollback + retry on failure
- [ ] Implement anti-skip safeguard: automatic catch-up if tick was missed
- [ ] Write test: re-running same tick input produces identical output

### C.4 Season lifecycle
- [ ] Generate fixture schedule for 22 match-days (12 teams, home & away)
- [ ] Implement season rollover sequence:
  1. Final fixture settlement
  2. Table/reward finalisation
  3. Transfer injection batch (24 special youth players)
  4. Contract/age transitions
  5. New season fixture generation
- [ ] Champions League qualification: top 2 from each first league → 32 clubs
- [ ] League cups: direct knockout for clubs not in UCL
- [ ] Ad event triggers: once at season start + once randomly mid-season

### C.5 Bot system
- [ ] Generate bot profiles with persona mix: transfer/training/balanced/ladder/youth = 25/20/25/15/15
- [ ] Implement core profile fields: `activeness_score`, `star_buyer_score`, `alliance_loyalty`, `timezone_profile`, `persona_type`, `risk_tolerance`, `social_talkativeness`
- [ ] Implement daily star injection: `daily_stars = base(200..1800) + activeness_score*8 + star_buyer_score*12 + league_tier_bonus + noise(±10%)`
- [ ] Implement alliance overbid control: `internal_overbid_chance = max(5%, 40% - 0.35 * loyalty)`
- [ ] Implement auction strategy pipeline (candidate list → persona utility score → alliance penalty → noise → bid/skip)
- [ ] Implement timezone-aware activity scheduling (online windows, session frequency, market checks)
- [ ] Implement lineup adaptation before lock windows
- [ ] Implement social behaviour: chat in global/private/group/alliance with template variation, delays, occasional typos/silence
- [ ] Implement watchlist late-bid behaviour in final 5 minutes
- [ ] Implement occasional suboptimal choices for human-like imperfection
- [ ] Implement random username/club name generation from preset lists (thousands of names)
- [ ] Implement bot replacement: when new human joins, delete a bot in a lower league
- [ ] Bots follow same API validations as humans — no hidden stat multipliers
- [ ] Sign bot actions by internal service identity; never expose bot flag via public API

---

## Phase D — Android App

### D.1 Asset extraction & project setup
- [ ] Extract usable assets from `plan/Goal Tactics - Football MMO_1.2.4_APKPure_src/` (drawables, icons, field images, splash)
- [ ] Create Android project: package `com.goaltactics.app`, min SDK 26, target SDK 34
- [ ] Set default orientation to `sensorLandscape`
- [ ] Configure theme: `GTTheme` (AppCompat NoActionBar, fullscreen)
- [ ] Set up design tokens: `gt_bg_dark=#1D2B03`, `gt_accent=#AFD50C`, `gt_text=#FFFFFF`, `gt_highlight=#FFFF00`, `gt_row_even=#641D2B03`, `gt_row_odd=#6492CC46`
- [ ] Add Roboto Bold as primary typeface
- [ ] Set up Retrofit + OkHttp for API communication (base URL: `https://gt.nikolai-linschmann.de/api/v1`)
- [ ] Set up WebSocket client for realtime events
- [ ] Set up Navigation component for fragment routing
- [ ] Set up ViewModels + StateFlow for reactive UI

### D.2 Shell & HUD
- [ ] Build `MainActivity` hosting `MainShellFragment`
- [ ] Build persistent left module menu (`RecyclerView`, 240 dp width)
- [ ] Build top title bar (bold white text, centred)
- [ ] Build bottom economy/action bar (★ stars, € money, 💊 medipacks + back/menu/context buttons)
- [ ] Wire `GET /hud/resources` to live-update economy HUD
- [ ] Wire `GET /bootstrap` on app launch for initial snapshot
- [ ] Implement `contentHost` FrameLayout for swapping feature fragments
- [ ] Implement lock banners (league lock 17:00–18:00 UTC, cup/UCL lock 12:00–13:00 UTC)
- [ ] Implement "queued for next match" state on post-lock lineup edit

### D.3 Auth & onboarding
- [ ] Build login screen (landscape split: login panel + quick-start + new-player buttons)
- [ ] Build registration screen
- [ ] Implement JWT storage and auto-refresh
- [ ] Implement new-player bootstrap (5,000,000₵ + 20,000★)

### D.4 Feature screens
- [ ] **Club**: my club, sponsors, in-game emails, accomplishments
- [ ] **Finances**: money history grid, stars history grid
- [ ] **Stadium**: buildings list, upgrade/speedup/deconstruct, unlimited seat extension UI
- [ ] **Squad**: player list table with alternating row shades, sell/upgrade/heal/skill-cards/rename/anti-age actions
- [ ] **Lineup**: football field background + 11 draggable player slots + bench + side player table + formation/tactic combo boxes + lock/queue indicators, next-3-match tabs
- [ ] **Training**: team training, individual slots (up to 5), camps with repeat pricing, tactics training (cap 150%), progress view
- [ ] **Scouting**: money scout / star scout / speedup UI, results list, sign action, probability state display
- [ ] **Transfer Market**: filterable auction table, favourites, own sales, bid UI, seasonal injections list
- [ ] **League**: fixtures, table, top scorers
- [ ] **Champions League**: fixtures, table, dedicated competition screen
- [ ] **Cups**: fixtures, bracket view
- [ ] **Ladder**: on-demand match trigger, stamina refill, ranking
- [ ] **Live match**: minute-by-minute event ticker via WebSocket
- [ ] **Friends**: friend list, search, requests, series ordering, public squad view
- [ ] **Chat**: global + private + paid groups (5,000★ creation) + alliance chat
- [ ] **Shop**: simulated grant buttons, ad event offers (100★/click, 200★ event mode), premium tier selection, skill-card bundles
- [ ] **Equipment**: shirts, emblems, perks activation/pricing
- [ ] **Alliances**: create (20,000★), join, members, chat, board, cup
- [ ] **Tasks**: onboarding, daily, weekly task lists with claim

### D.5 Reusable components
- [ ] No-data helper card (character image + message + primary/secondary action buttons)
- [ ] Confirmation popup for all economy-changing actions
- [ ] Alternating-row-shade table component via `RecyclerView` + `ListAdapter` + `DiffUtil`
- [ ] Pagination support for market, chat histories, ledger views
- [ ] Offline read cache with stale indicators

---

## Phase E — Web UI (Next.js)

### E.1 Project foundation
- [ ] Initialise Next.js App Router + TypeScript project
- [ ] Configure Tailwind CSS with GT design tokens (`#1D2B03`, `#AFD50C`, `#FFFFFF`, `#FFFF00`)
- [ ] Generate typed API client from OpenAPI spec
- [ ] Set up TanStack Query for data fetching/caching
- [ ] Set up auth store (JWT token + refresh), prefer HttpOnly refresh cookie
- [ ] Set up HUD store (stars/money/medipacks)
- [ ] Set up WebSocket client + realtime event dispatcher
- [ ] Configure service worker for cache and reconnect resilience
- [ ] Configure CSRF protection on state-changing endpoints
- [ ] Set strict Content Security Policy headers

### E.2 Shell & responsive layout
- [ ] Build shell: left nav menu, top title, bottom/sticky-top resource HUD
- [ ] Desktop: full landscape dashboard with persistent left menu + right detail panes
- [ ] Tablet: collapsible menu, two-pane for data-heavy views
- [ ] Mobile web: bottom tab shortcuts, expandable rows for dense tables

### E.3 Feature pages (full parity with Android)
- [ ] Auth: login, register, session refresh
- [ ] Club, sponsors, in-game emails, accomplishments
- [ ] Finances: money & stars history
- [ ] Stadium: buildings, upgrades, seats
- [ ] Squad: player list, actions (sell, upgrade, heal, skill-cards, anti-age)
- [ ] Lineup: drag-and-drop builder on football field, lock/queue behaviour, next-3-match selector
- [ ] Training: team/individual/camps/tactics
- [ ] Scouting: instruct, results, sign
- [ ] Transfer market: filterable table with realtime auction updates
- [ ] League: fixtures, table, top scorers
- [ ] Champions League & cups: fixtures, tables, brackets
- [ ] Ladder: on-demand match, ranking
- [ ] Live match: minute-by-minute feed
- [ ] Friends: list, search, requests, series, public squad view
- [ ] Chat: global, private, paid groups, alliance chat
- [ ] Shop: grant buttons, ad events, premium tiers, skill-card bundles
- [ ] Equipment: shirts, emblems, perks
- [ ] Alliances: create, join, members, board, cup
- [ ] Tasks: onboarding, daily, weekly

### E.4 Management / admin pages
- [ ] Admin dashboard with deep health check (`GET /admin/health/deep`)
- [ ] Manual tick trigger (`POST /admin/ticks/run`)
- [ ] Manual bot cycle trigger (`POST /admin/bots/run-cycle`)
- [ ] Season rollover control (`POST /admin/seasons/rollover`)
- [ ] Precompute trigger (`POST /admin/precompute/run?competition=…`)
- [ ] Training tick manual run / catch-up (`POST /admin/training-tick/run`, `/catchup`)
- [ ] Transfer injection trigger (`POST /admin/transfer/injections/run`)

### E.5 SEO & public pages
- [ ] Public landing / marketing page (SSR, structured metadata)
- [ ] FAQ and changelog pages
- [ ] Game pages: authenticated, `noindex`

---

## Phase F — Full Integration & Simulation

### F.1 End-to-end integration tests
- [ ] Register new user → bootstrap → verify 5,000,000₵ + 20,000★
- [ ] Create club → scout players → build squad
- [ ] Set lineup → verify lock at 17:00 UTC → verify precompute → verify 18:00 kickoff publish
- [ ] Cup/UCL lock at 12:00 UTC → kickoff at 13:00 UTC
- [ ] Friendly auto-cancel on cup/UCL conflict day
- [ ] Training tick at 00:00 UTC → verify strength changes → verify audit rows
- [ ] Transfer market: list player → bot bids → auction resolution
- [ ] Alliance creation → bot joins → alliance cup lineup
- [ ] Chat: send/receive in global, private, group, alliance channels via WebSocket
- [ ] Ladder: trigger on-demand match → verify immediate result
- [ ] Shop grant → verify ledger entry → verify daily cap enforcement
- [ ] Tasks: complete daily task → claim reward → verify wallet update

### F.2 Multi-season simulation
- [ ] Run automated 3-season simulation with 12 clubs (mix of human-test + bots)
- [ ] Verify season rollover: table rewards, transfer injections, contract/age transitions, new fixtures
- [ ] Verify Champions League qualification (top 2 per league)
- [ ] Verify cup bracket generation for non-UCL clubs
- [ ] Verify bot economy: star injection rates, overbid frequencies, no economy distortion
- [ ] Verify player progression curves: talent-10 near-cap trajectory, age-30+ decay, anti-age protection
- [ ] Verify no player exceeds strength 1000
- [ ] Verify no player age exceeds 34
- [ ] Verify determinism: replay precompute with same seed → identical results
- [ ] Verify catch-up: simulate missed training tick → automatic recovery with no duplicates

### F.3 Performance & load testing
- [ ] API response time < 200 ms p95 for read endpoints
- [ ] Precompute completes within scheduled window for all leagues
- [ ] WebSocket supports concurrent connections for all active users + bots
- [ ] Database query performance with 6+ months of partitioned data

---

## Phase G — Harden, Docs & Delivery

### G.1 Infrastructure & deployment
- [ ] Create `systemd` service units: `gt-api.service`, `gt-sim.service`, `gt-bot.service`, `gt-worker.service`, `gt-rt.service`
- [ ] Configure Nginx reverse proxy: `gt.nikolai-linschmann.de` → Next.js (:3000), `/api/*` → FastAPI (:8000), `/realtime` → WebSocket gateway
- [ ] Set up TLS via Certbot
- [ ] Enable UFW firewall; lock DB/Redis to localhost
- [ ] Configure PostgreSQL WAL archiving to `/mnt/website/GT/backups/wal/`
- [ ] Configure nightly full backup to `/mnt/website/GT/backups/base/` (retain 14 days)
- [ ] Configure archive Postgres on `/mnt/website/GT/archive-pgdata/`
- [ ] Create maintenance scripts: `precreate_partitions.sh`, `archive_partitions.sh`, `export_cold.sh`, `backup_rotate.sh`
- [ ] Set up manifest and verification scripts in `/mnt/website/GT/scripts/`
- [ ] Verify RPO ≤ 15 minutes, RTO ≤ 1 hour
- [ ] Run one full restore drill from backup

### G.2 Observability & monitoring
- [ ] Implement structured logging across all services
- [ ] Set up alerts: free disk space (70% warn / 85% critical), failed backups, missed partition moves, failed verification
- [ ] Monitor training tick: daily median gain by age bucket, % players above 700/900, tick runtime/retries, skipped/catch-up count
- [ ] Monitor bot KPIs: auction participation share, price inflation by tier, chat distribution, win rates, internal overbid frequency
- [ ] Monitor economy KPIs: daily stars minted vs spent, reward-cap hit rate, auction price inflation, premium adoption
- [ ] Monitor match engine: precompute runtime, playback delivery latency
- [ ] Frontend error tracking (Sentry or equivalent)
- [ ] Core Web Vitals dashboard for web client

### G.3 Security hardening
- [ ] All economic updates are server-authoritative
- [ ] Precompute artifacts signed/checksummed
- [ ] No client-submitted stat deltas are trusted
- [ ] Anti-automation throttling for sensitive actions
- [ ] Cap queued training operations per day
- [ ] Validate all training purchases against ownership and cooldown
- [ ] Reject duplicate requests via idempotency keys
- [ ] Encrypt backups at rest; restrict access to mounted storage paths; sign manifests
- [ ] Pre-kickoff result access restricted (results in separate column until kickoff)

### G.4 Documentation
- [ ] API reference (auto-generated from OpenAPI)
- [ ] Architecture decision records (ADRs) for key choices
- [ ] Runbook: deployment, rollback, backup restore, missed-tick recovery
- [ ] Game design document: all formulas, constants, and rules in one place
- [ ] Bot system configuration guide
- [ ] Admin operations guide (manual ticks, season rollover, injection triggers)
- [ ] Onboarding guide for new developers

### G.5 Final delivery checklist
- [ ] All Phase A–F checklist items complete
- [ ] CI pipeline green (lint + build + test) for backend, Android, web
- [ ] No critical or high security vulnerabilities open
- [ ] Production database migrated and seeded with initial data + bot accounts
- [ ] All 5 systemd services running and healthy
- [ ] Nginx serving web client and proxying API/WebSocket
- [ ] TLS certificate valid and auto-renewing
- [ ] Backup pipeline verified end-to-end
- [ ] Monitoring dashboards and alerts active
- [ ] Smoke test: register → play one full day cycle → verify all systems
