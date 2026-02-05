# Solución al Error de Base de Datos

## Problema Detectado

```
OperationalError: no such column: institucion_almacenregional.created_at
```

### Causa Raíz
Los modelos heredan de `TimeStampedModel` que agrega campos `created_at` y `updated_at`, pero las migraciones existentes en la base de datos no reflejan estos cambios.

### Solución Recomendada

#### Opción 1: Reset Completo de Base de Datos (DESARROLLO)

```bash
# 1. Detener el servidor Django si está corriendo
# Ctrl+C en la terminal del servidor

# 2. Eliminar la base de datos
cd backend
Remove-Item db.sqlite3 -Force

# 3. Eliminar archivos de migración problemáticos (OPCIONAL)
# Solo si las migraciones están corruptas
Remove-Item */migrations/0*.py -Exclude __init__.py

# 4. Recrear migraciones
python manage.py makemigrations

# 5. Aplicar todas las migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Cargar datos de prueba
python create_test_subalmacenes.py

# 8. Probar QR generation
python test_qr_generation.py
```

#### Opción 2: Migración Manual (PRODUCCIÓN)

```bash
# 1. Crear backup
cp db.sqlite3 db.sqlite3.backup

# 2. Generar migraciones
python manage.py makemigrations

# 3. Revisar SQL generado
python manage.py sqlmigrate institucion XXXX

# 4. Aplicar migraciones
python manage.py migrate

# 5. Verificar integridad
python manage.py check
```

## Estado Actual

- ✅ Modelos `Subalmacen` y `SolicitudTraslado` creados
- ✅ Campos QR agregados
- ✅ Serializers y ViewSets implementados
- ✅ Endpoints de aprobación creados
- ✅ Diagramas de arquitectura completos
- ❌ **Base de datos desincronizada**

## Próximos Pasos

1. **CRÍTICO:** Resolver problema de base de datos
2. Ejecutar `test_qr_generation.py` exitosamente
3. Validar generación de QR codes
4. Probar endpoints de aprobación
5. Merge a master

## Notas

- El archivo `db.sqlite3` está bloqueado por un proceso
- Necesitas cerrar cualquier conexión activa a la base de datos
- Considera usar PostgreSQL en producción para evitar problemas de bloqueo
