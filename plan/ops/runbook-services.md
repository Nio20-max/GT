# Services Runbook

## Installed systemd units

- `gt-api.service`
- `gt-scheduler.service`
- `gt-bot-worker.service`
- `gt-web.service`

## Common operations

- Start all:
  - `systemctl start gt-api gt-scheduler gt-bot-worker gt-web`
- Stop all:
  - `systemctl stop gt-web gt-bot-worker gt-scheduler gt-api`
- Restart all:
  - `systemctl restart gt-api gt-scheduler gt-bot-worker gt-web`
- Status:
  - `systemctl --no-pager --full status gt-api gt-scheduler gt-bot-worker gt-web`

## Health checks

- API health: `curl http://127.0.0.1:8000/health`
- API bootstrap: `curl http://127.0.0.1:8000/api/v1/bootstrap`
- Web: `curl http://127.0.0.1:3000`
