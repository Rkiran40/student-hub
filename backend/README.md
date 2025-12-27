# Flask Backend (SQLite) for StudentHub

This is a lightweight Flask backend to support the StudentHub frontend. It provides:
- JWT-based auth (signup, login, refresh, me)
- Student endpoints: upload files, list uploads, update profile
- Admin endpoints: list students, approve/suspend/activate students, manage uploads
- Uses SQLite for development (configurable via DATABASE_URL)
- File uploads stored on disk in `backend/uploads/`

Quick start (Windows / PowerShell):

1. Create venv and install deps

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

2. Copy example env

   copy .env.example .env
   # edit .env to set JWT_SECRET_KEY

3. Run server

   python -m backend.app

The server runs on http://localhost:5000 by default.

Notes:
- Email flows are stubbed (they return success for dev). Replace with a real SMTP provider for production.
- Admin access is protected by an `admin` role on `users.role`. Use DB seed or update a user to role `admin` to access admin endpoints.

To seed an admin with the credentials used here run (from project root):

```powershell
python backend/scripts/seed_admin.py --email admin@nuhvin.com --username admin@nuhvin.com --password 123456 --force
```

