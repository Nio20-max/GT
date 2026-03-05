#!/usr/bin/env bash
set -euo pipefail

ts=$(date -u +"%Y%m%dT%H%M%SZ")
out_dir="/mnt/website/GT/backups/base/${ts}"
mkdir -p "${out_dir}"
manifest="${out_dir}/backup-manifest.json"

pg_user="${PGUSER:-gt}"
pg_host="${PGHOST:-localhost}"
pg_port="${PGPORT:-5432}"

if command -v pg_basebackup >/dev/null 2>&1; then
  if pg_basebackup -h "${pg_host}" -p "${pg_port}" -U "${pg_user}" -D "${out_dir}" -Fp -Xs -P; then
    printf '{"status":"ok","ts":"%s","path":"%s"}\n' "${ts}" "${out_dir}" >"${manifest}"
  else
    printf '{"status":"failed","ts":"%s","path":"%s","reason":"pg_basebackup_failed"}\n' "${ts}" "${out_dir}" >"${manifest}"
  fi
else
  printf '{"status":"skipped","ts":"%s","path":"%s","reason":"pg_basebackup_missing"}\n' "${ts}" "${out_dir}" >"${manifest}"
fi

echo "created ${out_dir}"
