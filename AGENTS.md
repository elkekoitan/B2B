# Repository Guidelines

> Concise guide for building, testing, and contributing to this repo.

## Project Structure & Module Organization
- `app/`: FastAPI backend (models, services). Entrypoint: `app/main.py`.
- `agent_orchestrator/`: agents + orchestrator (`main.py`).
- `frontend/`: React + Vite (TypeScript) UI.
- `supabase/`: SQL migrations; `mock_data/` for local data.
- Ops: `docker-compose*.yml`, Dockerfiles, `Makefile`, `scripts/`.
- Docs & Logs: `docs/`, `logs/`.
- Tests: Python `test_*.py` at repo root or under `app/`.

## Build, Test, and Development Commands
- `make up` / `make down`: start/stop full Docker stack; `make logs` tails all.
- Backend dev: `make backend-dev` (hot‑reload FastAPI at proxy).
- Lint/format/CI: `make lint` (ruff), `make fmt` (black), `make ci` (checks).
- Backend tests: `make test-backend` or `docker compose exec backend pytest -q`.
- Frontend dev: `cd frontend && pnpm dev` (or `docker compose exec frontend npm run dev`).
- Reverse proxy: `http://localhost:8080` (UI `/`, API `/api/*`).

## Coding Style & Naming Conventions
- Python: Black + Ruff per `pyproject.toml` (line length 100, py311), 4‑space indent.
- Naming: `snake_case` functions/vars; `PascalCase` classes; sorted imports (Ruff I‑rule).
- TypeScript/React: ESLint + Prettier, 2‑space indent; `PascalCase` components; `camelCase` hooks/utils; colocate under `frontend/src/`.

## Testing Guidelines
- Framework: `pytest`; name files `test_*.py` near code or at repo root.
- Run: `make test-backend` (preferred) or exec `pytest` in backend container.
- Coverage: prioritize new code paths + critical logic; include happy‑path and error cases.
- Frontend: `pnpm lint`; use `pnpm test`/`npm test` if configured.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (e.g., `feat(api): add RFQ template`, `fix(ui): handle null offers`). Keep scope small, imperative mood.
- PRs: clear description, link issues, include test logs and screenshots when relevant.
- Gate: ensure `make lint` and tests pass; CI checks PR title format. See `CONTRIBUTING.md` if present.

## Roadmap & Tracking Alignment
- Tracking: follow `docs/PROJECT_TRACKING.md` for active items; align work with "Devam Eden" and "Sıradaki Adımlar".
- Roadmap: reference `docs/B2B_AGENTIK_DEVELOPMENT_ROADMAP.md` in PR descriptions (e.g., `[Phase 1] RBAC`, `[Phase 1] Catalog UI`).
- PR linkage: quote the relevant section/task from `PROJECT_TRACKING.md` and update its checklist upon merge.

## Security & Configuration Tips
- Copy `.env.example` → `.env` (or `.env.mock` for local mock). Never commit secrets.
- Required keys: Supabase, SMTP, Redis.
- DB migrations: `supabase/migrations/`; apply via `scripts/db_migrate_psql.sh`.
- CORS/ports: configured in `docker-compose.yml` and `app/main.py`.

## Agent‑Specific Instructions
- Orchestrator: `cd agent_orchestrator && python main.py` (local) or via Docker; requires `REDIS_URL` and Supabase env.
- Logs: backend `logs/backend.log`; agents `/app/logs/agents.log` and `/app/logs/main.log` (mounted to `./logs/`).
- Orchestration API: `POST /orchestrate` with `{ "job_type": "rfq_process", "rfq_id": "<uuid>", "payload": {} }`; `GET /orchestrate/status/{job_id}`; `DELETE /orchestrate/{job_id}`.
