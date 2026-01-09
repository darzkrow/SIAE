@echo off
REM Script para ejecutar pruebas del sistema de inventario (Windows)
REM Uso: run_tests.bat [opción]

setlocal enabledelayedexpansion

echo.
echo 🧪 Sistema de Pruebas - Inventario Hidroeléctrica
echo ==================================================
echo.

REM Opción por defecto
set OPTION=%1
if "%OPTION%"=="" set OPTION=all

if "%OPTION%"=="all" (
    echo Ejecutando todas las pruebas...
    python manage.py test inventario -v 2
    goto end
)

if "%OPTION%"=="models" (
    echo Ejecutando pruebas de modelos...
    python manage.py test inventario.tests -v 2
    goto end
)

if "%OPTION%"=="api" (
    echo Ejecutando pruebas de API...
    python manage.py test inventario.test_api -v 2
    goto end
)

if "%OPTION%"=="movements" (
    echo Ejecutando pruebas de movimientos...
    python manage.py test inventario.tests.MovimientoInventarioTests -v 2
    goto end
)

if "%OPTION%"=="coverage" (
    echo Ejecutando pruebas con cobertura...
    coverage run --source=inventario manage.py test inventario
    echo.
    echo Reporte de cobertura:
    coverage report
    echo.
    echo Generando reporte HTML en htmlcov\index.html
    coverage html
    goto end
)

if "%OPTION%"=="seed" (
    echo Generando datos de prueba...
    python manage.py seed_test_data
    goto end
)

if "%OPTION%"=="clean" (
    echo Limpiando base de datos...
    python manage.py flush --no-input
    echo Base de datos limpiada
    goto end
)

if "%OPTION%"=="help" (
    echo.
    echo Opciones disponibles:
    echo   all          - Ejecutar todas las pruebas
    echo   models       - Ejecutar solo pruebas de modelos
    echo   api          - Ejecutar solo pruebas de API
    echo   movements    - Ejecutar solo pruebas de movimientos
    echo   coverage     - Ejecutar pruebas con cobertura
    echo   seed         - Generar datos de prueba
    echo   clean        - Limpiar datos de prueba
    echo   help         - Mostrar esta ayuda
    echo.
    goto end
)

echo Opción no reconocida: %OPTION%
echo Usa: run_tests.bat help

:end
echo.
echo ✅ Completado
