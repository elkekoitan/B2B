#!/usr/bin/env bash
set -euo pipefail

# Apply all SQL migrations in supabase/migrations to a Postgres database via psql.
# Usage:
#   DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require \
#   ./scripts/db_migrate_psql.sh

if ! command -v psql >/dev/null 2>&1; then
  echo "psql is required. On Ubuntu: sudo apt-get update && sudo apt-get install -y postgresql-client" >&2
  exit 1
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL env var is required" >&2
  exit 1
fi

shopt -s nullglob
files=(supabase/migrations/*.sql)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No migration files found in supabase/migrations" >&2
  exit 0
fi

for f in $(ls -1 supabase/migrations/*.sql | sort); do
  echo "Applying migration: $f"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
done

echo "All migrations applied successfully."

