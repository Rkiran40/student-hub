# Run Alembic migrations against configured DATABASE_URL in backend/.env.dev or env
$env:DATABASE_URL = $env:DATABASE_URL
python -m alembic upgrade head
Write-Host 'Migrations applied.'
