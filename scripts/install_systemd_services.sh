#!/usr/bin/env bash
set -euo pipefail

install -d /etc/gt
if [[ ! -f /etc/gt/gt.env ]]; then
  cat >/etc/gt/gt.env <<'EOF'
GT_APP_ENV=production
GT_DB_URL=postgresql://gt:gt@localhost:5432/gt
EOF
fi

install -m 0644 deploy/systemd/gt-api.service /etc/systemd/system/gt-api.service
install -m 0644 deploy/systemd/gt-scheduler.service /etc/systemd/system/gt-scheduler.service
install -m 0644 deploy/systemd/gt-bot-worker.service /etc/systemd/system/gt-bot-worker.service
install -m 0644 deploy/systemd/gt-web.service /etc/systemd/system/gt-web.service

systemctl daemon-reload
systemctl enable --now gt-api.service
after_api_status=$(systemctl is-active gt-api.service || true)
echo "gt-api.service: ${after_api_status}"

systemctl enable --now gt-scheduler.service
systemctl enable --now gt-bot-worker.service
systemctl enable --now gt-web.service

systemctl --no-pager --full status gt-api.service gt-scheduler.service gt-bot-worker.service gt-web.service | cat
