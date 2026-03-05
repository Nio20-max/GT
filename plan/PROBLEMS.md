# Problems Log

## 2026-03-05

All listed issues were fixed in this pass.

1. Auth storage/token hardening: resolved.
   - Implemented PBKDF2 password hashing, expiring random tokens, and token cleanup.
   - Evidence: `backend/app/services/auth_store.py`
2. Login auto-create bypass: resolved.
   - Login now fails on unknown user and invalid password instead of creating accounts.
   - Evidence: `backend/app/services/auth_store.py`
3. Insecure register defaults: resolved.
   - Register now requires validated username/email/password and returns conflict for duplicates.
   - Evidence: `backend/app/api/routes.py`
4. Contract placeholder responses: resolved.
   - Replaced generic placeholder marker flow with stateful contract handling and deterministic feature payloads.
   - Evidence: `backend/app/api/routes.py`
5. Hardcoded simulation secret: resolved.
   - Simulation secret moved to config (`GT_SIMULATION_SERVER_SECRET`) and consumed from settings.
   - Evidence: `backend/app/core/config.py`, `backend/app/services/runtime_state.py`
6. Archive script placeholder: resolved.
   - Implemented real archive behavior: compress, checksum, manifest, retention cleanup.
   - Evidence: `backend/scripts/ops/archive_partitions.sh`
7. Android main layout parity gap: resolved for main shell structure.
   - Main layout now mirrors original `mainlayout.xml` structure/IDs closely while staying build-safe.
   - Evidence: `android/app/src/main/res/layout/gt_mainlayout_shell.xml`

## Verification

1. Backend tests passed: `17 passed`.
2. Android build passed: `:app:assembleDebug` successful.
3. Web build passed: `next build` successful.
4. Live API endpoint verification passed: `Summary: passed=150 failed=0`.
5. Live auth smoke test passed: register `201`, login `200`.
