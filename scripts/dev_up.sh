#!/usr/bin/env bash
set -e

docker compose -f docker-compose.dev.yml up -d --build
# Wait a few seconds for migrations
sleep 6
# Seed admin inside backend
docker compose -f docker-compose.dev.yml exec -T backend python backend/scripts/seed_admin.py --email admin@local --username admin --password adminpass --force

echo "Dev stack is up. Frontend at http://localhost:5173, backend at http://localhost:5001"
