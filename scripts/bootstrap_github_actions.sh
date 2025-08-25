#!/usr/bin/env bash
set -euo pipefail

# This script bootstraps GitHub Actions secrets and triggers the DB migrate and Deploy workflows.
# Requirements:
# - GitHub CLI installed and authenticated: https://cli.github.com/
# - Run this script from the repo root (or pass --repo owner/name)
# - Fill the env vars below or export them before running.

usage() {
  cat << USAGE
Usage: ./scripts/bootstrap_github_actions.sh [--repo owner/name]

Environment variables to set (example values):
  SSH_HOST=1.2.3.4
  SSH_USER=ubuntu
  SSH_KEY="$(cat ~/.ssh/id_ed25519)"
  SSH_PORT=22
  DATABASE_URL="postgresql://user:pass@db.supabase.co:5432/postgres?sslmode=require"
  APP_ENV_FILE="$(cat << 'EOF'
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
VITE_API_URL=
EOF
)"

Examples:
  SSH_HOST=1.2.3.4 SSH_USER=ubuntu SSH_KEY="$(cat ~/.ssh/id_ed25519)" \
  DATABASE_URL=postgresql://... APP_ENV_FILE="$(cat .env.prod)" \
  ./scripts/bootstrap_github_actions.sh --repo yourname/yourrepo

USAGE
}

REPO=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"; shift; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required. Install from https://cli.github.com/" >&2
  exit 1
fi

if [[ -z "${REPO}" ]]; then
  # Try to infer from git remote
  if git remote get-url origin >/dev/null 2>&1; then
    origin=$(git remote get-url origin)
    # formats: https://github.com/owner/name.git or git@github.com:owner/name.git
    REPO=$(printf "%s" "$origin" | sed -E 's#(git@github.com:|https://github.com/)##; s/\.git$//')
  fi
fi

if [[ -z "${REPO}" ]]; then
  echo "--repo owner/name is required (or set git remote origin)." >&2
  exit 1
fi

required=(SSH_HOST SSH_USER SSH_KEY DATABASE_URL APP_ENV_FILE)
for v in "${required[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    echo "Missing required env: $v" >&2
    usage
    exit 1
  fi
done

# Optional: SSH_PORT
SSH_PORT=${SSH_PORT:-22}

echo "Setting GitHub Actions secrets on $REPO ..."
gh secret set SSH_HOST --repo "$REPO" --body "$SSH_HOST"
gh secret set SSH_USER --repo "$REPO" --body "$SSH_USER"
gh secret set SSH_KEY  --repo "$REPO" --body "$SSH_KEY"
gh secret set SSH_PORT --repo "$REPO" --body "$SSH_PORT"
gh secret set DATABASE_URL --repo "$REPO" --body "$DATABASE_URL"
gh secret set APP_ENV_FILE  --repo "$REPO" --body "$APP_ENV_FILE"

echo "Secrets set. Triggering DB migration..."
gh workflow run db-migrate.yml --repo "$REPO"

echo "Waiting 15s before deploy..."
sleep 15

echo "Triggering Deploy workflow..."
gh workflow run deploy.yml --repo "$REPO"

echo "Done. Check GitHub Actions runs for progress."

