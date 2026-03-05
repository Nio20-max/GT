# Problems Log

## 2026-03-05

1. Web dependency baseline currently uses `next@15.0.0` and npm reports a critical advisory in this version line.
   - Suggested remediation: update to patched Next.js release and re-run build + smoke tests.
2. Many gameplay endpoints are contract-complete but still backed by deterministic in-memory or placeholder behavior rather than fully persistent domain services.
   - Suggested remediation: migrate each module (transfer/scouting/social/tasks/alliances) to database-backed services and add end-to-end tests.
3. Backup hook can emit a failure manifest if PostgreSQL auth or runtime config is incomplete for `pg_basebackup`.
   - Suggested remediation: configure dedicated backup role and credentials in `/etc/gt/gt.env` for production backups.
