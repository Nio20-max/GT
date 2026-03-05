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

## Runtime state backup scripts

- Backup runtime state and optional PostgreSQL dump:
	- `bash backend/scripts/ops/backup_runtime_state.sh`
- Restore runtime state and optional PostgreSQL dump:
	- `bash backend/scripts/ops/restore_runtime_state.sh /path/to/backup`

The backup script writes checksums (`SHA256SUMS`) for quick integrity verification.

## Runtime observability checks

- Metrics snapshot: `curl http://127.0.0.1:8000/api/v1/admin/metrics/runtime`
- Execute due scheduler windows: `curl -X POST http://127.0.0.1:8000/api/v1/admin/scheduler/run-due`
- Recent settlements: `curl http://127.0.0.1:8000/api/v1/admin/settlements`
