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