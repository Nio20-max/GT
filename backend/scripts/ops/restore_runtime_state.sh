#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="$1"
STATE_DIR="${GT_STATE_DIR:-/tmp/gt-state}"

if [[ ! -d "${BACKUP_DIR}" ]]; then
  echo "Backup directory not found: ${BACKUP_DIR}" >&2
  exit 1
fi

if [[ -f "${BACKUP_DIR}/SHA256SUMS" ]]; then
  (cd "${BACKUP_DIR}" && sha256sum -c SHA256SUMS)
fi

mkdir -p "${STATE_DIR}"
if [[ -f "${BACKUP_DIR}/state-json.tar.gz" ]]; then
  tar -xzf "${BACKUP_DIR}/state-json.tar.gz" -C "${STATE_DIR}"
fi

if [[ -n "${GT_DB_URL:-}" ]] && [[ -f "${BACKUP_DIR}/db.sql" ]] && command -v psql >/dev/null 2>&1; then
  psql "${GT_DB_URL}" -f "${BACKUP_DIR}/db.sql"
fi

echo "Restore completed from ${BACKUP_DIR}"
