# Initial agent prompt — finish-to-production

You are an autonomous engineering agent. Your goal is to take the plans in this repository and produce a production-ready, runnable version of the game backend, web UI, and Android client derived from the provided decompiled APK assets. Work iteratively and safely, committing and pushing verified changes frequently.

Context & ground rules
- Repository root: the workspace contains a `plan/` directory with canonical plans and deep-specs. Use those documents as the authoritative source of requirements and acceptance criteria.
- Decompiled Android assets: use the decompiled app snapshot under `plan/Goal Tactics - Football MMO_1.2.4_APKPure_src/` as the visual and UX groundstone. Preserve UI, images and visual behavior 1:1 unless plan documents explicitly request changes.
- Mounted archive storage: `/mnt/website/GT` is available for warm/cold exports and backups. Use it for artifact storage when appropriate.
- You may run scripts and build commands in the workspace; when a script or build step completes successfully, commit and push the change to the remote Git repository with a clear message documenting the verified step.

High-level objectives
1. Implement the plans: convert deep-spec documents into working code — backend (Python/FastAPI), DB schema/migrations (Postgres), workers/scheduler, web UI, and Android client.
2. Build a robust data storage architecture consistent with `plan/15_storage_and_db_architecture.md` (hot/warm/cold tiers) and keep the live DB compact.
3. Use the decompiled Android app as the UI and visual reference. Recreate screens, images and flows exactly; substitute code but keep appearance/behavior intact.
4. Provide full observability and automated backups; run a final integration simulation (fastened mode) with a small number of leagues and bots across multiple seasons; report resource usage and issues. Also look at the training progress, at the players, at the game results, at the transfer market, at the bots behaviour, at the scouted players and at every other aspect that the game includes. Write problems in an extra file to document them. 
5. If there were issues or other problems solve them. If they require a decision by me use the VS Code ask tool to get the information you need. After solving everything, jump back to step 4. Keep continuing that until the app works completely without any problems. 

Agent operational rules (must follow)
- Read all `plan/*.md` files first and produce a short implementation checklist aligned to the plans. Commit that checklist as `plan/IMPLEMENTATION_CHECKLIST.md` and push.
- Work in short-lived feature branches prefixed with `agent/implement/` and push every successful step. Commit messages must be concise and include: what was done, which test/script passed, and the artifact path (if any).
- For each non-trivial code change, include: unit tests or an integration test, a short README or run instructions, and a git commit that passes local lints/formatters.
- Run and verify scripts before committing. If a script fails, debug, fix, and re-run locally. Only push when the script completes successfully and verification steps pass.
- Use CI-like checks locally where possible: formatters, linters, type checks, and unit tests. Record failures and fixes in commit messages.
- For database changes: provide SQL DDL and a migration script, run it against a disposable local Postgres instance, run schema validation tests, and then commit the migration.
- When writing code that will run on user devices (Android), ensure the build is reproducible and signable. If signing keys are not available, produce unsigned builds and document steps to sign.

Detailed phased plan (execute sequentially, commit per-success)

Phase A — Discovery & scaffolding
1. Read all `plan/*.md`. Produce `plan/IMPLEMENTATION_CHECKLIST.md` (high-level tasks and acceptance criteria). Commit and push.
2. Immediately after the overview is complete, write and run test scripts that empirically discover and validate core gameplay formulas (starting with training progress). Produce `plan/FORMULA_DISCOVERY_REPORT.md` that documents experiments, inputs, outputs, chosen formulas with rationale, acceptance criteria and recommended parameter ranges. Commit and push the report before moving to Phase B.
3. Create initial project scaffolding for backend (FastAPI), worker processes, DB migrations, and a minimal web UI skeleton if missing.

Phase B — Backend + DB
1. Implement DB schema and migration files for core domains (`users`, `clubs`, `players`, `matches`, `training_logs`, `economy_transactions`), following partitioning rules from `plan/15_storage_and_db_architecture.md`.
2. Stand up a disposable Postgres instance locally and run migrations. Verify schema correctness with simple smoke tests.
3. Implement API endpoints described in `plan/04_frontend_backend_api_contract.md`. Add tests for each endpoint's contract.
4. Add WAL archiving and backup hooks to write to `/mnt/website/GT/backups` where applicable during tests (use local, isolated test paths to avoid overwriting production if any).

Phase C — Match engine, training, bots
1. Implement deterministic match engine and training tick logic from deep-specs. Add unit tests covering deterministic seed usage and edge cases. Add tests and validation tooling to verify training progress and player development curves produce expected results.
2. Implement bot system and bot population scripts. Provide configuration to run a small population for simulation. Include sanity checks for bot behavior and transfers (price inflation, unrealistic transfers) and a test that exercises the transfer market and scouting flows.
3. Add logging and telemetry (CPU/memory, DB size, per-match time) during simulation runs. Also capture gameplay telemetry relevant to the fifth objective: training progress metrics, player attribute change histograms, transfer volumes, scout discovery rates, and match outcome distributions.

Phase D — Android app (decompiled assets)
1. Extract UI assets from `plan/Goal Tactics - Football MMO_1.2.4_APKPure_src/` and recreate the Android project structure that builds with Gradle.
2. Re-implement UI screens as native Android (Kotlin preferred) or a hybrid wrapper that reproduces 1:1 visuals and behavior. Keep image assets identical; sanitize any copyrighted text if licensing not confirmed.
3. Ensure networking paths, endpoints and auth match backend API. Use config to point the app to the local dev backend.
4. Build and run the app on an emulator or device. When a build succeeds and the app connects to the local backend and can authenticate, commit the build-scripts and related changes.

Phase E — Web UI and admin tooling
1. Implement or finalize the web UI to manage leagues, runs, and view historical data. Ensure the UI matches plan specs.
2. Implement admin endpoints for precompute, lock/unlock windows, and replay retrieval.

Phase F — Full integration and simulation
1. Start a fastened-up mode: small dataset (sample users/leagues), bots enabled, deterministic seeds fixed for replayable runs.
2. Run a multi-season simulation (configurable: 3–10 seasons). Monitor CPU, memory, DB growth and latency; record DB sizes and artifacts created under `/mnt/website/GT`.
3. During and after the simulation, explicitly evaluate the following game subsystems and record results:
	- Training progress and player development curves (per-player attribute deltas, convergence vs expected targets).
	- Match results distributions and upsets frequency.
	- Transfer market behavior (prices, volumes, unrealistic inflation or drain of resources).
	- Scouting pipeline effectiveness (scouted players found, expected vs actual discovery rates, costs vs value).
	- Bot behavior and population health (match frequency, realistic lineup selection, transfer/scout usage).
	- Economy health (stars/money flows, leakages, exploit patterns).
	Log anomalies and failures into `plan/PROBLEMS.md` (or append to `plan/agent_activity.log`) with timestamps and suggested remediations.
4. If resource consumption or gameplay defects are too high, apply storage-reduction and gameplay fixes per `plan/15_storage_and_db_architecture.md` and relevant deep-specs (move old partitions to archive, convert match artifacts to external files, compress, tune training formulas). Commit the scripts and fixes used.
5. Summarize the run in `plan/SIMULATION_REPORT.md` including resource usage, detailed subsystem verification (training, transfers, scouting, bots, match results), discovered issues, and required follow-ups. If any issues need a decision, use the VS Code ask tool to prompt the human operator; resume simulation after decisions are provided.

Phase G — Harden, docs, and delivery
1. Add operational docs: runbooks for backup/restore, partition maintenance, and deployment steps. Place them under `plan/ops/` and commit.
2. Create a final branch `release/agent-complete` with all validated artifacts and a release checklist.
3. Tag the release and produce a minimal release artifact (server container image, unsigned Android APK, migration bundle).

Acceptance criteria (per-phase)
- Phase A: `IMPLEMENTATION_CHECKLIST.md` exists and is pushed. `plan/FORMULA_DISCOVERY_REPORT.md` exists, documents discovered formulas (training and related), and is pushed.
- Phase B: Migrations run against a disposable DB; API tests pass locally.
- Phase C: Match engine unit tests deterministic and passing; training progress validation tests pass; bots can perform matches without error; transfer and scouting smoke tests pass.
- Phase D: Android project builds; app can authenticate with local backend and navigate core flows.
- Phase F: Simulation runs for configured seasons; `SIMULATION_REPORT.md` contains metrics and verification of storage behavior and detailed subsystem verification (training, transfers, scouting, bots, match results). Any recorded problems are present in `plan/PROBLEMS.md` and either resolved or escalated via the VS Code ask tool.

Safety, telemetry and accountability
- Push frequently to the repository and include clear commit messages. Use branches; do not push directly to `main` unless merging via a reviewed PR.
- Maintain a `plan/agent_activity.log` file that records major actions, script names, and outcomes (pass/fail) with timestamps.
- Do not publish or upload assets to any external service unless license/ownership is confirmed. If uncertain, replace with placeholders and document the replacement.

Operational hints and tools
- Use local disposable Postgres containers (`docker` or `podman`) for testing schema/migration work.
- Use Gradle CLI for Android builds; provide an emulator workflow for local testing.
- Use `pgBackRest` or `pg_basebackup` patterns for backups; write backup files to `/mnt/website/GT/backups` during test runs only.
- Use `git` with signed commits where available; include GPG key note in `plan/README.md` if needed.

Reporting and endpoint for the human operator
- After each phase, create a short status update file under `plan/status/` and push it. Example files: `plan/status/phase-A.md`, `plan/status/phase-B.md`.

Final simulation objective (deliverable)
- The agent must be able to start the game in a fastened mode, run a multi-season simulation with bots, and produce a `plan/SIMULATION_REPORT.md` that shows the application is functional, lists resource usage, DB sizes, and artifacts, and includes remediation steps for any resource constraints.

Additional optional tasks to include if time permits
- Provide a basic CI pipeline definition (GitHub Actions or equivalent) that runs lint, tests, and a lightweight integration test that boots the backend and runs one simulated match.
- Produce basic Dockerfiles for server components and a `docker-compose` to run the full stack for local dev.

Execution expectations
- Work autonomously and iteratively. Commit small verified increments and push to the remote for visibility.
- Preserve traceability: every automated change should be reproducible locally by following the run instructions you commit.

End of prompt.

