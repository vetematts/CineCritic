#!/usr/bin/env bash

# Render start script: apply migrations/seed data before launching gunicorn.
# Running migrations on each deploy keeps the hosted database in sync with the codebase.

set -o errexit
set -o pipefail

echo "Applying database migrations..."
flask db upgrade

echo "Seeding demo data (skips if records already exist)..."
flask ops seed || true

echo "Starting gunicorn..."
exec gunicorn "main:app" --bind 0.0.0.0:${PORT:-5000}
