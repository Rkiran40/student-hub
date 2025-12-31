# PowerShell helper to bring up dev stack and run seeds
docker compose -f docker-compose.dev.yml up -d --build
# Wait a bit for backend to finish migrations
Start-Sleep -s 5
# Seed admin (use the existing seed script)
docker compose -f docker-compose.dev.yml exec -T backend python backend/scripts/seed_admin.py --email admin@local --username admin --password adminpass --force
Write-Host 'Dev stack is up. Frontend at http://localhost:5173, backend at http://localhost:5001'