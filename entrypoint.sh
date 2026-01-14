#!/bin/sh
set -e

# Ensure static/media directories are writable by the app user (useful when volumes are created as root)
echo "Fixing ownership for static and media..."
chown -R appuser:appuser /app/staticfiles /app/media || true

echo "Running migrations (if DB available)..."
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting server as appuser: $@"
# Drop privileges to `appuser` for the final command
exec runuser -u appuser -- "$@"
