#!/usr/bin/env bash
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL not set. You can set it or create backend/.env.dev and add DATABASE_URL there."
  exit 1
fi

python -m alembic upgrade head

echo "Migrations applied."
