# Deployment checklist

This document lists the steps to deploy the application to staging/production.

## Environment variables (required)
- DATABASE_URL (e.g., mysql+pymysql://user:pass@host:3306/dbname?charset=utf8mb4)
- SECRET_KEY (secure random string)
- JWT_SECRET_KEY (secure random string)
- DEBUG=0
- TESTING=0
- ENABLE_DEBUG_ENDPOINTS=0
- DEV_SQLITE_FALLBACK=0
- UPLOAD_FOLDER=/var/app/uploads

## Steps
1. Build Docker images (CI should handle this): use the `publish` workflow.
2. Run Alembic migrations:
   - `alembic -c backend/alembic.ini upgrade head` (or use provided scripts/run_migrations.sh)
3. Start services (docker-compose, Kubernetes manifests, etc.)
4. Run pre-deploy checks:
   - `python scripts/predeploy_check.py` (will exit non-zero when critical issues are present)
5. Run smoke tests:
   - `python scripts/smoke_test.py` against the deployed endpoints
6. Optionally run the E2E smoke test (signup -> admin approve -> login):
   - `ADMIN_EMAIL=<admin> ADMIN_PASSWORD=<pass> python scripts/e2e_smoke.py`
7. Verify login/signup/E2E flows in staging (seed an admin or use an onboarding flow)

## Rollback
- Keep a tracked image tag for each deploy so you can re-deploy previous tag.
- Ensure DB backups are available and restore plan is tested.

## Notes
- The app will NOT automatically fall back to SQLite in production unless `DEV_SQLITE_FALLBACK` is intentionally enabled.
- The `/debug/*` endpoints are disabled by default in production; enable only for internal troubleshooting using `ENABLE_DEBUG_ENDPOINTS=1`.
