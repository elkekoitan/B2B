#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.coolify.yml}
ENV_FILE=${ENV_FILE:-.env}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker and retry." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  if [[ -f .env.mock ]]; then
    cp .env.mock "$ENV_FILE"
    echo "Created $ENV_FILE from .env.mock (mock mode)"
  else
    echo "Missing $ENV_FILE and .env.mock" >&2
    exit 1
  fi
fi

echo "Building and starting using $COMPOSE_FILE and $ENV_FILE ..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo "Done. UI: http://localhost:13000 | API: http://localhost:18000"

