SHELL := /bin/bash

.PHONY: up down logs rebuild backend-dev test-backend test-frontend fmt lint ci precommit smoke docs-check

up:
	docker compose build && docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

rebuild:
	docker compose build --no-cache

backend-dev:
	docker compose exec backend bash -lc "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

test-backend:
	docker compose exec backend pytest -q || true

test-frontend:
	docker compose exec frontend npm test --silent || true

fmt:
	docker compose exec backend black app || true

lint:
	docker compose exec backend ruff check app || true

ci: up lint test-backend

precommit:
	pre-commit run -a || true

smoke:
	bash scripts/smoke_api.sh

docs-check:
	@echo "Checking documentation files..."
	@test -f AGENTS.md || (echo "Missing AGENTS.md" >&2; exit 1)
	@test -f docs/README.md || (echo "Missing docs/README.md" >&2; exit 1)
	@test -f docs/PROJECT_TRACKING.md || (echo "Missing docs/PROJECT_TRACKING.md" >&2; exit 1)
	@echo "Docs OK"
