# 5) Website Plan (Playable Full Feature Parity)

Goal:
- A browser client with full feature parity to mobile app.
- Same backend API and same economy/simulation rules.

Locked schedule behavior on web:
- League lock/precompute: 17:00 UTC -> kickoff playback at 18:00 UTC.
- Cup/UCL lock/precompute: 12:00 UTC -> kickoff playback at 13:00 UTC.
- Friendly slot: 13:00 UTC unless cup/UCL conflict.
- Training updates applied at 00:00 UTC.

Suggested stack:
- Next.js (App Router) + TypeScript
- Tailwind or CSS modules + design tokens from mobile style
- WebSocket client for chat/live events
- Service worker for cache and reconnect resilience

## Product architecture
1. Shell layer
- Left nav menu, top title, bottom resource HUD (or sticky top HUD for desktop)
- Route-level feature pages loaded into shell container

2. Feature modules
- Club, finances, stadium, squad, lineup, training, scouting
- Transfer market, league, ladder, friends, live, chat, shop
- Champions League and Cups
- Alliances (chat, board, cup)
- Tasks (onboarding/daily/weekly)
- Premium and perk management

3. Shared state
- Auth store (token + refresh)
- HUD store (stars/money/medipacks)
- Realtime event dispatcher

4. Data access
- Typed API client generated from OpenAPI
- Query caching (TanStack Query)
- Optimistic updates only for safe UI actions

## Responsive behavior
Desktop:
- Full landscape-like dashboard with persistent left menu and right detail panes.

Tablet:
- Collapsible menu, two-pane for data-heavy views.

Mobile web:
- Bottom tab shortcuts for key modules.
- Simplify dense tables with expandable rows.

## Key UX patterns to preserve from APK
- Always visible economy status.
- No-data helper cards with action buttons.
- Table-heavy operations in transfer and squad modules.
- Lineup drag/drop on football field.
- Bright CTA buttons for confirmations.

## Technical plan by milestone
1. Web foundation
- Auth, shell, HUD, bootstrap endpoint integration
- Basic pages: club, finances, squad

2. Management core
- Lineup builder with drag/drop
- Training, scouting, stadium modules

3. Market and competition
- Transfer market realtime updates
- League/fixtures/tables/live match feed
- Champions League and league cups with 13:00 UTC slot behavior

4. Social and parity completion
- Friends, friendly requests, chat
- Shop grants endpoint and equipment/perks
- Alliances and alliance cup workflows
- Tasks and premium entitlement UI

5. Hardening
- E2E tests
- performance budgets
- accessibility pass

## SEO and discoverability
- Public landing pages only (marketing, FAQ, changelog)
- Game pages authenticated and noindex
- Structured metadata for acquisition pages

## Security for web client
- HttpOnly refresh cookie (preferred)
- CSRF protection on state-changing endpoints
- strict content security policy
- anti-automation throttling for sensitive actions

## Deployment on current server
- Build artifacts to `/var/www/gt-web`
- Serve by Nginx reverse proxy:
  - `gt.nikolai-linschmann.de` -> Next.js service (`localhost:3000`)
  - `/api/*` proxied to FastAPI (`localhost:8000`)
  - `/realtime` proxied to websocket gateway

## Observability
- Frontend error tracking (Sentry or AppCenter web)
- Core web vitals dashboard
- API latency and websocket reconnect metrics
