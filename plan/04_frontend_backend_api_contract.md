# 4) API Access Points Frontend Needs

Base URL:
- `https://gt.nikolai-linschmann.de/api/v1`

Auth:
- JWT bearer token
- `Idempotency-Key` header for write actions

Global runtime rules reflected by API:
- Official league matches: 18:00 UTC, lock/precompute 17:00 UTC
- Cup/UCL matches: 13:00 UTC, lock/precompute 12:00 UTC
- Friendly slot: 13:00 UTC, cancelled on cup/UCL conflict
- Training tick: 00:00 UTC, reports: 08:00 Europe/London

## Auth and account
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /me/profile`
- `PATCH /me/profile`
- `GET /me/settings`
- `PATCH /me/settings`

## Bootstrap and shell
- `GET /bootstrap`
  - returns user + club snapshot + unread counts + menu badges
- `GET /hud/resources`
  - stars, money, medipacks, active cooldowns
- `GET /notifications/unread-count`
- `GET /runtime/calendar`
  - next lock times and kickoff times per competition
- `GET /runtime/locks`
  - current lock status for lineup/tactics

## Club and sponsors
- `GET /club`
- `PATCH /club/name`
- `GET /club/accomplishments`
- `GET /club/fans-members`
- `GET /club/season-history`
- `GET /club/all-time-tables`
- `GET /sponsors/offers`
- `POST /sponsors/{offerId}/accept`
- `GET /emails`
- `GET /emails/{emailId}`
- `POST /emails/{emailId}/read`
- `DELETE /emails/{emailId}`

## Finances
- `GET /finances/summary`
- `GET /finances/history?days=30`
- `GET /finances/ledger?cursor=...`
- `GET /finances/stars-history?days=30`

## Stadium
- `GET /stadium`
- `GET /stadium/buildings`
- `POST /stadium/buildings/{buildingId}/upgrade`
- `POST /stadium/buildings/{buildingId}/speedup`
- `POST /stadium/buildings/{buildingId}/deconstruct`
- `GET /stadium/seats/pricing`

## Squad and players
- `GET /squad`
- `GET /players/{playerId}`
- `POST /players/{playerId}/skill-cards/apply`
- `POST /players/{playerId}/upgrade`
- `POST /players/{playerId}/rename`
- `POST /players/{playerId}/change-origin`
- `POST /players/{playerId}/heal`
- `POST /players/{playerId}/sell`
- `GET /players/{playerId}/anti-age-upgrade-options`
- `POST /players/{playerId}/anti-age-upgrade`

## Lineup and tactics
- `GET /lineup/current`
- `PUT /lineup/current`
- `GET /lineup/upcoming?limit=3`
- `PUT /lineup/upcoming/{fixtureId}`
- `GET /tactics`
- `PUT /tactics`
- `GET /lineup/lock-status/{fixtureId}`
- `POST /lineup/queue-change/{fixtureId}`

## Training
- `GET /training/overview`
- `POST /training/team`
- `POST /training/individual`
- `POST /training/camps/{campId}/book`
- `POST /training/tactics/{tacticId}/train`
- `GET /training/progress?playerId=...`
- `GET /training/formulas`
- `GET /training/individual-tiers`
- `GET /training/camps/{campId}/repeat-cost`

## Scouting
- `GET /scouting/overview`
- `POST /scouting/instruct`
- `POST /scouting/instruct-special`
- `POST /scouting/speedup`
- `GET /scouting/results`
- `POST /scouting/results/{resultId}/sign`
- `GET /scouting/probability-state`

## Transfer market
- `GET /transfer/auctions?filters=...`
- `GET /transfer/auctions/{auctionId}`
- `POST /transfer/auctions/{auctionId}/bid`
- `POST /transfer/auctions/{auctionId}/favorite`
- `DELETE /transfer/auctions/{auctionId}/favorite`
- `GET /transfer/my-sales`
- `GET /transfer/my-bids`
- `GET /transfer/favorites`
- `GET /transfer/seasonal-injections`

## League and matches
- `GET /league/current`
- `GET /league/table`
- `GET /league/fixtures`
- `GET /league/results`
- `GET /league/topscorers`
- `GET /matches/{matchId}`
- `GET /matches/{matchId}/live`
- `GET /matches/{matchId}/report`
- `POST /matches/{matchId}/live/substitute`
- `POST /matches/{matchId}/live/change-formation`

## Champions League and cups
- `GET /ucl/current`
- `GET /ucl/fixtures`
- `GET /ucl/table`
- `GET /cups/current`
- `GET /cups/fixtures`
- `GET /cups/bracket`

## GT ladder
- `GET /ladder/overview`
- `GET /ladder/fixtures`
- `POST /ladder/matches/{matchId}/start`
- `POST /ladder/stamina/refill`
- `GET /ladder/ranking`

## Friends and social
- `GET /friends`
- `POST /friends/search`
- `POST /friends/requests/{managerId}`
- `POST /friends/requests/{requestId}/accept`
- `POST /friends/requests/{requestId}/decline`
- `DELETE /friends/{friendId}`
- `POST /friendlies/invite`
- `GET /friendlies/requests`
- `GET /friends/series`
- `PUT /friends/series`
- `GET /clubs/{clubId}/public-squad`

## Chat and realtime
- `GET /chat/channels`
- `GET /chat/channels/{channelId}/messages?cursor=...`
- `POST /chat/channels/{channelId}/messages`
- `POST /chat/groups`
- `GET /chat/private/{managerId}`
- `WS /realtime`
  - topics: chat, live-match-events, notifications, market-updates

## Shop and rewards (no ads/IAP now)
- `GET /shop/catalog`
- `POST /shop/offers/{offerId}/grant`
  - grants the configured amount immediately (simulated purchase/reward)
- `GET /shop/grants/history`
- `GET /shop/events`
- `GET /shop/premium/tiers`
- `POST /shop/premium/{tierId}/grant`

## Equipment and cosmetics
- `GET /equipment/catalog`
- `POST /equipment/shirts/{id}/buy`
- `POST /equipment/emblems/{id}/buy`
- `POST /equipment/perks/{id}/activate`
- `GET /equipment/perks/pricing`

## Alliances
- `POST /alliances`
- `GET /alliances/{allianceId}`
- `POST /alliances/{allianceId}/join-request`
- `POST /alliances/{allianceId}/members/{memberId}/approve`
- `POST /alliances/{allianceId}/members/{memberId}/kick`
- `GET /alliances/{allianceId}/chat`
- `GET /alliances/{allianceId}/board`
- `POST /alliances/{allianceId}/board/threads`
- `GET /alliances/{allianceId}/cup`
- `POST /alliances/{allianceId}/cup/lineup`

## Tasks
- `GET /tasks/onboarding`
- `GET /tasks/daily`
- `GET /tasks/weekly`
- `POST /tasks/{taskId}/claim`

## Admin/ops endpoints (internal)
- `POST /admin/ticks/run`
- `POST /admin/bots/run-cycle`
- `POST /admin/seasons/rollover`
- `GET /admin/health/deep`
- `POST /admin/precompute/run?competition=league|cup|ucl`
- `POST /admin/training-tick/run`
- `POST /admin/training-tick/catchup`
- `POST /admin/transfer/injections/run`

## Common response envelopes
- Success:
```json
{ "ok": true, "data": {"...": "..."}, "traceId": "..." }
```
- Error:
```json
{ "ok": false, "error": { "code": "INSUFFICIENT_STARS", "message": "..." }, "traceId": "..." }
```

## Event contracts for WebSocket
- `hud.updated`
- `chat.message.created`
- `transfer.auction.updated`
- `match.live.event`
- `notification.created`
- `fixture.locked`
- `match.precomputed`
- `task.completed`
- `alliance.updated`
