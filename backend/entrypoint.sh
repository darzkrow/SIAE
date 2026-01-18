#!/bin/sh
set -e

# Variables para la espera de la base de datos
DB_HOST="db"
DB_PORT="5432"
MAX_RETRIES=30
RETRY_INTERVAL=2

# Bucle de espera para la base de datos
echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
retries=0
while ! nc -z "${DB_HOST}" "${DB_PORT}" && [ ${retries} -lt ${MAX_RETRIES} ]; do
    retries=$((retries+1))
    echo "Waiting for database connection... (${retries}/${MAX_RETRIES})"
    sleep ${RETRY_INTERVAL}
done

if ! nc -z "${DB_HOST}" "${DB_PORT}"; then
    echo "Database connection failed after ${MAX_RETRIES} retries. Exiting."
    exit 1
fi

echo "Database is ready. Continuing with startup..."

# Los comandos se ejecutan como root para tener permisos, luego se delega al usuario de la aplicación
echo "Running migrations (if DB available)..."
runuser -u appuser -- python manage.py migrate --noinput

echo "Collecting static files..."
runuser -u appuser -- python manage.py collectstatic --noinput

echo "Starting server..."
# El comando final se ejecuta con 'exec' para que reemplace el proceso del script
# y reciba las señales del sistema (como SIGTERM para detenerse)
exec runuser -u appuser -- "$@"

