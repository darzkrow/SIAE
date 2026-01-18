#!/bin/sh
set -e

# Ensure static/media directories are writable by the app user (useful when volumes are created as root)
echo "Fixing ownership for static and media..."
chown -R appuser:appuser /app/staticfiles /app/media || true

echo "Running migrations (if DB available)..."
runuser -u appuser -- python manage.py migrate --noinput

echo "Collecting static files..."
runuser -u appuser -- python manage.py collectstatic --noinput

echo "Starting server..."
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application

