# Storage and Database Architecture

This document defines a concrete hot/warm/cold storage architecture, exact PostgreSQL build choices, partitioning and archival workflows, backup and recovery runbook, and an implementation sequence that uses the mounted archive storage at `/mnt/website/GT` for infrequently accessed data and backups.

**Goals**
- Keep the primary (hot) Postgres small and fast for gameplay operations.
- Provide a warm archive Postgres instance for infrequent historical queries.
- Use `/mnt/website/GT` as the local cold/warm storage for archives, exports, and backups.
- Provide robust backup, verification and recovery procedures (RPO/RTO targets defined).

---

**Target Architecture (three tiers)**

1. Primary Postgres (hot)
   - Purpose: live gameplay reads/writes (current season + recent history required for gameplay and UI responsiveness).
   - Storage: fast local NVMe/SSD on the DB host (not on `/mnt/website/GT`).
   - Data kept: `users`, `clubs`, `players`, `squads`, `current_leagues`, recent partitions of time-series tables.

2. Archive Postgres (warm)
   - Purpose: ad-hoc historical queries and reporting for older periods.
   - Storage: PostgreSQL data directory placed under `/mnt/website/GT/archive-pgdata` on the mounted volume.
   - Data kept: detached monthly partitions moved from primary (ex: matches older than 6 months).

3. Cold files + backups (cold)
   - Purpose: long-term retention, compressed exports, base backups and WAL archives.
   - Storage: `/mnt/website/GT/backups/`, `/mnt/website/GT/exports/`, manifests and scripts.

Directory layout on the mounted storage (suggested)

```
/mnt/website/GT/
  archive-pgdata/
  backups/
    base/
    wal/
  exports/
    matches/
    training/
    economy/
  manifests/
  scripts/
```

---

Exact PostgreSQL build choices (recommended)

- PostgreSQL 15+ (use latest stable v15/16 available in your environment).
- Primary instance: tuned for high IOPS and low latency (local NVMe). Enable WAL archiving to mounted storage.
- Archive instance: data_directory set to `/mnt/website/GT/archive-pgdata`; tuned for larger storage and lower CPU priority.
- Use `pgBackRest` or `pg_basebackup` + WAL archiving; `pgBackRest` preferred for staged retention and compression.

---

Schema and partitioning strategy

1. Table classification
- Hot forever: `users`, `clubs`, `players`, `squads`, `league_configs`, `settings`.
- Time-series high-volume: `matches`, `match_events`, `training_logs`, `economy_transactions`, `scouting_logs`, `notifications`.
- Large artifact storage: store compact summaries in DB; store large replay/blobs externally under `/mnt/website/GT/exports` and reference by `artifact_path` and `hash` in DB.

2. Partitioning
- Use monthly range partitions on `created_at` for `matches`, `match_events`, `training_logs`, `economy_transactions`.
- Pre-create next month partitions as part of maintenance jobs to avoid on-the-fly partition creation.

3. Retention on primary (example policy — tune to needs):
- `matches`, `match_events`: keep last 6 months hot
- `training_logs`: keep last 3 months hot
- `economy_transactions`: keep last 12 months hot
- Older partitions are detached and moved to archive.

4. Indexing
- On hot partitions: only indexes required for gameplay and UI queries (avoid many complex indexes on every partition).
- On archive: use BRIN indexes for very large append-only tables and low selectivity queries; keep only necessary B-tree indexes (`club_id`, `created_at`).

5. Row shaping & compression
- Favor narrow columns over big JSON blobs; store stable schema where possible.
- Compress large JSON blobs before persisting (application-level gzip or use `pg_backrest` compression for backups).
- Keep event granularity practical (do not store every micro-step of simulation forever).

---

Archival workflow (automated monthly job)

1. Partition lifecycle job (monthly)
- Pre-create next-month partition(s).
- For each table with expired partitions (older than policy):
  - Detach partition from primary (use `ALTER TABLE ... DETACH PARTITION`).
  - Create a manifest entry: table, partition_name, row_count, checksum, created_at.
  - Copy partition data into archive DB using `pg_dump --data-only` or `INSERT INTO archive_db.table SELECT * FROM detached_partition` over a secure connection. Prefer `COPY` for bulk speed.
  - Verify row counts and checksums between source partition and archive destination.
  - After verification, drop the detached partition from primary.

2. Warm → Cold (e.g., > 24 months)
- Export archive partitions to compressed Parquet/CSV (`zstd` compression recommended) and place under `/mnt/website/GT/exports/<table>/<YYYY-MM>.parquet.zst`.
- Record manifest: file path, rows, checksum, schema_version, moved_at.
- Optionally delete the rows from the archive DB after verifying archived file integrity.

3. Artifact handling
- For match replays/blobs: write them directly to `/mnt/website/GT/exports/matches/` on creation or move them as part of the monthly export. Store only `artifact_path` and `artifact_hash` in the DB.

---

Backup and recovery runbook (robust setup)

1. Backup schedule
- Full base backup: nightly to `/mnt/website/GT/backups/base/` (retain 14 days by default).
- WAL archiving: continuous to `/mnt/website/GT/backups/wal/` with retention for 14 days (for PITR up to retention window).
- Archive DB backups: weekly full backup; monthly long retention backups.

2. Retention policy (example)
- WAL retention: 14 days
- Daily full backups: 14 days
- Weekly full backups: 8 weeks
- Monthly full backups: 12 months

3. Targets and SLAs
- RPO: <= 15 minutes (WAL cadence and upload).
- RTO: <= 1 hour for primary restore onto prepared host (assumes base backup available and WAL archives reachable).

4. Verification and drills
- Nightly: verify backup file integrity (checksums) and WAL archiving success.
- Weekly: run a dry restore test for a small recent backup into an isolated instance and run basic smoke queries.
- Monthly: full restore drill of an older weekly backup to validate long-term retention.

---

Operational guardrails and monitoring

- Filesystem checks: ensure `/mnt/website/GT` supports required semantics (`fsync`, stable write ordering). Avoid unreliable network mounts without write guarantees.
- Alerts: free space thresholds (70% warn, 85% critical), failed backups, missed partition moves, failed verification.
- Autovacuum tuning: aggressive on hot tables, lighter on archive instance.
- Query routing: application-level routing — live gameplay reads/writes go to primary; historical reports read from archive.
- Security: encrypt backups at rest, restrict access to the mounted path, sign manifests.

---

Concrete implementation sequence (step-by-step)

1. Provision DB hosts
   - Primary: high-IO host with NVMe.
   - Archive: host with `/mnt/website/GT/archive-pgdata` mounted and sized for expected archive growth.

2. Install PostgreSQL 15+ and backup tooling (`pgBackRest` or `wal-e`, `pg_dump` for exports`).

3. Implement schema changes
   - Create partitioned tables for `matches`, `match_events`, `training_logs`, `economy_transactions`.
   - Implement artifact column `artifact_path` and `artifact_hash` for large blobs (or move to separate artifact store table).

4. Add maintenance jobs (systemd timers / cron / Airflow)
   - `precreate_partitions.sh` — create next month partitions
   - `archive_partitions.sh` — detach, copy to archive DB, verify, drop
   - `export_cold.sh` — export >24m partitions to Parquet and checksum
   - `backup_rotate.sh` — manage retention for base + WAL

5. Implement manifest and verification scripts in `/mnt/website/GT/scripts`.

6. Configure WAL archiving to `/mnt/website/GT/backups/wal` and nightly `pgBackRest` full backup to `/mnt/website/GT/backups/base`.

7. Run verification drills (one full restore test + one archive rehydrate test).

8. Place monitoring/alerts for disk, WAL, backup success, and job failures.

---

Capacity and effect

- Expect primary DB size to fall substantially (commonly 60–90% smaller than keeping all history hot), depending on retention windows.
- Use earlier per-user storage estimates to forecast growth; offload older match artifacts and partitions to `/mnt/website/GT` to cap growth.

---

Notes and tradeoffs

- Mounted storage reliability: local-attached mounted volumes are OK for warm/cold tier; avoid using unstable network mounts as a primary DB data directory unless the filesystem semantics are known and reliable.
- Query latency for archive: acceptable tradeoff — archive DB on mounted storage will be slower but fine for infrequent reports.
- Compliance and retention: keep manifests and checksums to support audits and restoration requirements.

---

Next actions I can take for you

- Generate exact SQL DDL templates for monthly partitioned tables (e.g., `matches`, `training_logs`).
- Create the shell scripts for partition precreate, archive+verify+drop, and export to Parquet, placing them in `/mnt/website/GT/scripts`.
- Produce a `pgBackRest` configuration targeting `/mnt/website/GT/backups`.

Choose which of the above you'd like next.
