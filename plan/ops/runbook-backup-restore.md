# Backup And Restore Runbook

## Base backup hook

- Script: `backend/scripts/ops/backup_hook.sh`
- Output root: `/mnt/website/GT/backups/base/`

## Archive hook

- Script: `backend/scripts/ops/archive_partitions.sh`
- Output root: `/mnt/website/GT/exports/`

## Execution

- `bash backend/scripts/ops/backup_hook.sh`
- `bash backend/scripts/ops/archive_partitions.sh`

## Restore notes

- For real restore drills, use production-grade backup tooling (`pgBackRest` or `pg_basebackup` + WAL replay) and verify RPO/RTO targets from storage plan.
