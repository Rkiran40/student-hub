# Makefile for common dev tasks
.PHONY: up down build migrate seed smoke test logs

# Use docker compose dev by default
COMPOSE_FILE = docker-compose.dev.yml

up:
	docker compose -f $(COMPOSE_FILE) up -d --build
	@echo "Stack started. Frontend: http://localhost:5173 Backend: http://localhost:5001"

down:
	docker compose -f $(COMPOSE_FILE) down

build:
	docker compose -f $(COMPOSE_FILE) build --no-cache

migrate:
	# Apply migrations using local environment or the compose env
	python -m alembic upgrade head

seed:
	# Seed admin user in running backend container
	docker compose -f $(COMPOSE_FILE) exec -T backend python backend/scripts/seed_admin.py --email admin@local --username admin --password adminpass --force

smoke:
	python scripts/smoke_test.py

test:
	python -m pytest backend/tests -q -r a

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

# staging helper
staging-up:
	docker compose -f docker-compose.staging.yml up -d --build

staging-down:
	docker compose -f docker-compose.staging.yml down
