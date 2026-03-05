#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${1:-/mnt/website/GT/backups/runtime}"
STATE_DIR="${GT_STATE_DIR:-/tmp/gt-state}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="${BACKUP_DIR}/${STAMP}"

mkdir -p "${OUT_DIR}"

if [[ -d "${STATE_DIR}" ]]; then
  tar -czf "${OUT_DIR}/state-json.tar.gz" -C "${STATE_DIR}" .
fi

if [[ -n "${GT_DB_URL:-}" ]] && command -v pg_dump >/dev/null 2>&1; then
  pg_dump "${GT_DB_URL}" > "${OUT_DIR}/db.sql"
fi

sha256sum "${OUT_DIR}"/* > "${OUT_DIR}/SHA256SUMS"
echo "Backup written to ${OUT_DIR}"
