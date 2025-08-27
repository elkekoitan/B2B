# Repository Guidelines

## Project Structure & Module Organization
- Backend (FastAPI): `agentik-b2b-app/backend/app`
  - `api/` (routes), `core/` (auth, config, middleware), `models/`, `services/`, `tests/`
- Frontend (Vite + React + TS): `frontend/` (`src/pages`, `src/components`, `src/services`)
- Agents (Orchestrator): `agent_orchestrator/`
- Database (Supabase): `supabase/` (`tables/`, `migrations/`)
- CI/Docs: `.github/workflows/`, `docs/` (all docs centralized)

## Build, Test, and Development Commands
- Start stack (Docker): `make up`; logs: `make logs`
- Lint/Format: `make lint` (ruff), `make fmt` (black)
- Backend tests: `make test-backend` (pytest)
- Frontend dev: `cd frontend && pnpm dev`
- Manual Docker: `docker compose build && docker compose up -d`

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indent; `snake_case` for functions/vars, `PascalCase` for classes.
- Tools: Ruff (lint) + Black (format) via `pyproject.toml`.
- TypeScript/React: ESLint enabled; components in `PascalCase`, maintain consistent file naming.
- API: Routes under `app/api/routes/`, schemas in `app/models` (Pydantic v2).

## Testing Guidelines
- Backend: Pytest. Location: `agentik-b2b-app/backend/app/tests/`.
- Naming: files `test_*.py`, tests `test_*` functions.
- Run: `make test-backend` or `cd agentik-b2b-app/backend && pytest -q`.
- Prefer small unit tests; add lightweight integration tests with FastAPI TestClient + dependency overrides when needed.

## Commit & Pull Request Guidelines
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`. Keep messages imperative and concise; link issues (`#123`).
- PRs: summary, motivation, scope, screenshots for UI, updated docs when behavior/config changes.

## Security & Configuration Tips
- Never commit secrets. Copy `.env.example` to `.env` and set: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SMTP_*`, `VITE_API_URL`.
- Use envs via `app/core/config.py`. Validate inputs; respect RBAC (see `app/core/permissions.py`).
- For DB changes, add SQL under `supabase/migrations/` and keep `tables/` in sync.
