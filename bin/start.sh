#!/usr/bin/env bash

# Render start script: apply migrations/seed data before launching gunicorn.
# Running migrations on each deploy keeps the hosted database in sync with the codebase.

set -o errexit
set -o pipefail

echo "Applying database migrations..."
flask db upgrade

if [[ "${SKIP_SEED:-0}" != "1" ]]; then
  echo "Seeding demo data (skips if records already exist)..."
  flask ops seed || true
else
  echo "Skipping seed step because SKIP_SEED=1"
fi

echo "Starting gunicorn..."
exec gunicorn "main:app" --bind 0.0.0.0:${PORT:-5000}
