#!/bin/sh
set -e

DB_HOST="db"
DB_PORT="5432"
MAX_RETRIES=30
RETRY_INTERVAL=2

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

# Fix permissions for volumes if running as root
if [ "$(id -u)" = '0' ]; then
    echo "Fixing permissions for static and media volumes..."
    mkdir -p /app/staticfiles /app/media
    chown -R appuser:appuser /app/staticfiles /app/media
    
    # Execute the rest of the script as appuser
    echo "Running migrations as appuser..."
    gosu appuser python manage.py migrate --noinput
    
    echo "Collecting static files as appuser..."
    gosu appuser python manage.py collectstatic --noinput
    
    echo "Loading initial data if empty..."
    gosu appuser python manage.py shell -c "
from geography.models import State
from institucion.models import OrganizacionCentral
from catalogo.models import Marca
import os
import subprocess

if State.objects.count() == 0:
    print('Loading geography data...')
    subprocess.run(['python', 'manage.py', 'loaddata', 'venezuela_full.json'])

if OrganizacionCentral.objects.count() == 0:
    print('Loading institutional data...')
    subprocess.run(['python', 'manage.py', 'loaddata', 'organizacion_inicial.json'])

if Marca.objects.count() == 0:
    print('Loading popular brands...')
    subprocess.run(['python', 'manage.py', 'loaddata', 'marcas_populares.json'])
"
    
    echo "Starting server as appuser..."
    exec gosu appuser "$@"
else
    # Fallback if not root
    echo "Running as non-root user $(id -u)..."
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    
    echo "Loading initial data if empty..."
    python manage.py shell -c "
from geography.models import State
from institucion.models import OrganizacionCentral
from catalogo.models import Marca
import os
import subprocess

if State.objects.count() == 0:
    print('Loading geography data...')
    subprocess.run(['python', 'manage.py', 'loaddata', 'venezuela_full.json'])

if OrganizacionCentral.objects.count() == 0:
    print('Loading institutional data...')
    subprocess.run(['python', 'manage.py', 'loaddata', 'organizacion_inicial.json'])

if Marca.objects.count() == 0:
    print('Loading popular brands...')
    subprocess.run(['python', 'manage.py', 'loaddata', 'marcas_populares.json'])
"
    
    exec "$@"
fi
