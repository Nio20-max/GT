# GT Remake Setup Overview

Domain target: `gt.nikolai-linschmann.de`

Decided stack (from your answers):
- Backend: Python + FastAPI
- Database: PostgreSQL
- Deployment: direct `systemd` services (no containers for the game stack)
- Bots: enabled in production from day one
- Game cadence: 1 game day every 24h
- League size at launch: 12 clubs
- New manager start: 5,000,000 money + 20,000 stars
- Match simulation: deterministic core by seed + random cosmetic events
- Web scope: full feature parity with app

Locked runtime schedule:
- League matches: 18:00 UTC, lock + precompute at 17:00 UTC
- Cup/UCL matches: 13:00 UTC, lock + precompute at 12:00 UTC
- Friendly slot: 13:00 UTC, auto-cancelled when cup/UCL exists
- Ladder: on-demand immediate calculation
- Training gains: 00:00 UTC
- Ingame reports: 08:00 Europe/London

Feature scope alignment with `Goal Tactics.md`:
- Full v1: Champions League, league cups, alliances, private+group chat, perks, premium entitlements, tasks, bots in alliances.
- Women world: phase 2 with shared stars wallet.

## Project Artifacts Reviewed
- Product mindmap: `plan/Goal Tactics.md`
- Decompiled Android package: `plan/Goal Tactics - Football MMO_1.2.4_APKPure_src/`
- Runtime/server context from current host (Ubuntu VPS)

## Deliverables in this folder
1. `plan/01_apk_overview_and_ui_analysis.md`
   - Deep inventory of decompiled APK contents
   - Focus on UI and layout architecture with concrete XML snippets
2. `plan/02_backend_architecture_and_computation_plan.md`
   - Full backend domain model and computations
   - Scheduling/tick system
   - Bot strategy system and behavior modeling
   - No-ads and free-IAP replacement behavior
3. `plan/03_app_ui_rebuild_spec.md`
   - UI rebuild spec that preserves original visual language
   - Concrete implementation examples for Android/web parity
4. `plan/04_frontend_backend_api_contract.md`
   - Complete API surface proposal for app/web clients
5. `plan/05_web_client_plan.md`
   - Browser client architecture and rollout with full feature parity
6. `plan/06_current_server_inventory.md`
   - Hardware, software, services, and deployment notes for this host

## Recommended build order
1. Foundation
   - Create PostgreSQL schema and migration pipeline
   - Implement auth/session/player bootstrap
   - Build static game-data service (formations, skills, building curves)
2. Deterministic core engine
   - Training calculations, finances, building timers, scouting, transfer logic
   - Match engine with deterministic seed pipeline
3. Scheduling and messaging
   - Daily tick scheduler
   - Notification/ingame mail generation
   - Event queue + retry strategy
4. Multiplayer and bots
   - League orchestration, market competition, chat, friendships
   - Bot account generation and behavior workers
5. Clients
   - Android remake client and web parity client against same API
6. Ops hardening
   - systemd units, Nginx reverse proxy, TLS, monitoring, backups, and abuse controls

## Non-functional baseline
- All economic updates must be server-authoritative.
- Every state-changing endpoint must be idempotent or use action tokens.
- Keep deterministic simulation traces for disputes and debugging.
- Use event/audit logs for player economy and bot actions.
