#!/usr/bin/env bash
set -euo pipefail

HOST=${HOST:-localhost}
API_PORT=${API_PORT:-8000}
UI_PORT=${UI_PORT:-3000}
NGINX_PORT=${NGINX_PORT:-8080}

echo "== Smoke: Backend health =="
curl -fsS "http://$HOST:$API_PORT/health" | jq . || curl -fsS "http://$HOST:$API_PORT/health" || true

echo "== Smoke: Backend info =="
curl -fsSI "http://$HOST:$API_PORT/api/v1/info" | head -n 1 || true

echo "== Smoke: Frontend (direct) =="
curl -fsSI "http://$HOST:$UI_PORT/" | head -n 1 || true

echo "== Smoke: Nginx reverse proxy =="
curl -fsSI "http://$HOST:$NGINX_PORT/" | head -n 1 || true
curl -fsSI "http://$HOST:$NGINX_PORT/api/health" | head -n 1 || true

echo "== Smoke: Orchestrate (local) =="
curl -fsS -X POST "http://$HOST:$API_PORT/orchestrate" \
  -H 'Authorization: Bearer mock-admin-token' \
  -H 'Content-Type: application/json' \
  -d '{"job_type":"supplier_discovery","rfq_id":"demo"}' | jq . || true

echo "Done."
