# Game Start Blocked Items (Need Follow-up)

These are still missing for a true production game launch, but cannot be fully solved in a single local patch without larger architecture and rollout work.

## 1. PostgreSQL-Backed Persistence Layer
- Current status:
  - State is now persisted on disk JSON files for survivability.
- Why blocked:
  - Full migration to PostgreSQL repositories/transactions across all modules requires substantial service-layer rewrite and migration validation.
- Required next work:
  - Introduce DB access layer, map existing migrations to repositories, replace JSON persistence for auth/game/runtime paths.

## 2. Real Implementations for Most Gameplay Modules
- Current status:
  - Core onboarding (`/club`, `/squad`) and league read visibility are now real.
  - Many endpoints remain contract-state placeholders (transfer/scouting/social/shop/alliances/tasks).
- Why blocked:
  - Each module needs domain logic, persistence, and tests.
- Required next work:
  - Replace contract handlers endpoint-by-endpoint with domain services and DB-backed models.

## 3. Full Match Lifecycle and Economy Settlement
- Current status:
  - Precompute/publish and table/results visibility work from runtime state.
- Why blocked:
  - No complete settlement engine writing economy transactions, progression updates, rewards, and penalties across all competitions.
- Required next work:
  - Add deterministic settlement pipeline with idempotent writes and reconciliation jobs.

## 4. Realtime Event System
- Current status:
  - WebSocket endpoint is still a connect-and-close stub.
- Why blocked:
  - Needs event bus, publish pipeline, and client subscriptions for live gameplay updates.
- Required next work:
  - Implement topic event dispatch for live matches, chat, notifications, and market updates.

## 5. Full Frontend/Android Playability
- Current status:
  - Auth + navigation are working and cleaner.
  - Most gameplay views are still scaffold-level and not fully wired.
- Why blocked:
  - Requires substantial UI implementation and per-screen API integration.
- Required next work:
  - Implement complete gameplay pages/screens for squad, lineup, training, transfer, and league management.

## 6. Production Hardening and Operations
- Current status:
  - Systemd services and smoke scripts exist.
- Why blocked:
  - Needs operational guardrails beyond code changes.
- Required next work:
  - Add backup/restore drills, observability dashboards/alerts, rate limiting, and incident runbooks.
