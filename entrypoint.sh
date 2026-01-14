#!/bin/sh
set -e

# Simple entrypoint: run migrations and collectstatic, then exec the passed command
echo "Running migrations (if DB available)..."
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting server: $@"
exec "$@"
