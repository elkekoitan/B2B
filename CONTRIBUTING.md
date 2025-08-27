# Contributing Guide

Thank you for contributing to Agentik B2B. This guide summarizes how to set up, code, test, and open PRs. For day-to-day commands and structure, see `AGENTS.md`.

## Setup
- Clone and copy env: `cp .env.example .env` (or use `.env.mock`).
- Start stack: `make up`; logs: `make logs`.
- Optional: install pre-commit hooks: `pip install pre-commit && pre-commit install`.

## Coding Standards
- Python 3.11, FastAPI backend under `app/`; agents in `agent_orchestrator/`.
- Format and lint: Black + Ruff (see `pyproject.toml`).
- Frontend uses React + Vite + TypeScript, ESLint.

## Tests
- Backend: `make test-backend` (runs pytest). Add tests as `test_*.py`.
- Frontend: `pnpm lint`, `pnpm build` (tests if available).

## Commits & Pull Requests
- Use Conventional Commits for PR titles: `feat(api): ...`, `fix(ui): ...`.
- Ensure `make lint` and tests pass. Include screenshots for UI.
- Fill PR template: summary, changes, tests, and linked issues.

## Security
- Do not commit secrets. Use `.env` locally and GitHub Secrets in CI.
- Report vulnerabilities via `SECURITY.md`.

