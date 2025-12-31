# Project layout

This repository has been reorganized into two top-level folders:

- `frontend/` — Vite + React app. Run within this folder:
  - npm install: `npm ci --prefix frontend`
  - dev: `npm run dev --prefix frontend`
  - build: `npm run build --prefix frontend`

- `backend/` — Flask API. Run within this folder:
  - create venv: `python -m venv .venv && .venv\Scripts\pip.exe install -r requirements.txt`
  - run: `python -m backend.app`

Notes:
- `node_modules` has been moved under `frontend/` but you may delete and re-install locally if you run into permission issues: `rm -rf frontend/node_modules && npm ci --prefix frontend`.
- The repo root now contains only `.git`, `.gitignore`, and the `frontend/` & `backend/` folders.

If you want, I can also add a root `README.md` (instead of `README_ROOT.md`) or update `frontend/README.md` to include consolidated instructions.

## Local development with Docker (MySQL + backend + frontend dev)

1. Start the dev stack:

   - PowerShell: `scripts\dev_up.ps1`
   - Bash: `scripts/dev_up.sh`

   Or run directly:

   ```bash
   docker compose -f docker-compose.dev.yml up -d --build
   ```

2. The backend will be available at: `http://localhost:5001`
   The frontend dev server will be available at: `http://localhost:5173` (hot reload enabled).

3. The dev helper seeds an admin user at `admin@local` / password `adminpass` — change this in a real environment.

Makefile & smoke tests

- Use the provided `Makefile` for common dev tasks. Examples:
  - `make up` — build & start the dev stack
  - `make smoke` — run `scripts/smoke_test.py` against `http://localhost:5001` and `http://localhost:5173`
  - `make migrate` — apply Alembic migrations locally

- Smoke test scripts are in `scripts/` (`smoke_test.py`, `smoke_test.sh`, `smoke_test.ps1`). They use `BACKEND_URL` and `FRONTEND_URL` env vars, defaulting to `http://localhost:5001` and `http://localhost:5173`.

Staging Compose

- I added `docker-compose.staging.yml` to build backend and the production frontend (nginx) for staging environments. It binds the frontend to port `8080`.

Production readiness notes:
- Debug endpoints (e.g., `/debug/db`) are disabled by default in production. To temporarily enable them for internal troubleshooting, set `ENABLE_DEBUG_ENDPOINTS=1` in your staging/prod environment (use cautiously).
- The application will NOT automatically fall back to SQLite in production unless `DEV_SQLITE_FALLBACK` is intentionally enabled. Ensure `DATABASE_URL` is reachable and migrations are applied before promoting to production.
- See `DEPLOYMENT.md` for a concise deployment checklist and recommended pre-deploy items.
- I added `docker-compose.staging.yml` to build backend and the production frontend (nginx) for staging environments. It binds the frontend to port `8080`.

Notes:
- If you prefer local MySQL instead of Docker, create a DB and user and export `DATABASE_URL` before running the backend:

  ```sql
  CREATE DATABASE studenthub_db;
  CREATE USER 'username'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
  GRANT ALL PRIVILEGES ON studenthub_db.* TO 'username'@'localhost';
  FLUSH PRIVILEGES;
  ```

  Then export `DATABASE_URL=mysql+pymysql://username:password@localhost:3306/studenthub_db?charset=utf8mb4` and run the backend.

- To apply migrations manually:

  ```bash
  alembic upgrade head
  ```

- Before promoting to staging/production, run the pre-deploy checks:

  ```bash
  python scripts/predeploy_check.py
  ```
  The script will report warnings or errors for unsafe production configuration (e.g., DEBUG enabled, SQLite fallback enabled, missing `SECRET_KEY`).
