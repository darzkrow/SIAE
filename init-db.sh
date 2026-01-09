#!/bin/bash

# Script de inicialización de base de datos para GSIH Inventario
# Este script ejecuta migraciones, carga datos de prueba y crea superusuario

set -e

echo "🚀 Iniciando GSIH Inventario..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté disponible..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ PostgreSQL está disponible"

# Ejecutar migraciones
echo "📦 Ejecutando migraciones..."
python manage.py migrate

# Crear superusuario si no existe
echo "👤 Creando superusuario..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gsih.com', 'admin123')
    print("✅ Superusuario 'admin' creado")
else:
    print("ℹ️  Superusuario 'admin' ya existe")
END

# Cargar datos de prueba (opcional)
if [ "$LOAD_TEST_DATA" = "true" ]; then
    echo "📊 Cargando datos de prueba..."
    python manage.py seed_test_data
    echo "✅ Datos de prueba cargados"
fi

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Inicialización completada"
echo "🎉 GSIH Inventario está listo para usar"
