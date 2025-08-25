#!/usr/bin/env bash
set -euo pipefail

# Deploy the stack locally (or on a server) using docker-compose.coolify.yml
# Usage:
#   1) Create a .env with production values (see README or sample below)
#   2) Run: ./scripts/deploy_local_coolify.sh

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.coolify.yml}
ENV_FILE=${ENV_FILE:-.env}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install: https://docs.docker.com/engine/install/" >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose plugin is required. Install: https://docs.docker.com/compose/install/" >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  cat >&2 << EOF
Missing $ENV_FILE file. Create it with content like:

ENVIRONMENT=production
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
USE_MOCK_SUPABASE=false
USE_MOCK_REDIS=false
# VITE_API_URL can be left empty; frontend auto-targets http://<host>:18000
VITE_API_URL=
EOF
  exit 1
fi

echo "Building and starting services with $COMPOSE_FILE ..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo "Stack is starting. Check with: docker ps"
echo "Frontend: http://<server_ip>:13000  |  API: http://<server_ip>:18000"

