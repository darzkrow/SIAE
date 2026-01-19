#!/bin/bash

# Script para ejecutar pruebas del sistema de inventario
# Uso: ./run_tests.sh [opción]

set -e

echo "🧪 Sistema de Pruebas - Inventario Hidroeléctrica"
echo "=================================================="

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar opciones
show_help() {
    echo ""
    echo "Opciones disponibles:"
    echo "  all          - Ejecutar todas las pruebas"
    echo "  models       - Ejecutar solo pruebas de modelos"
    echo "  api          - Ejecutar solo pruebas de API"
    echo "  movements    - Ejecutar solo pruebas de movimientos"
    echo "  coverage     - Ejecutar pruebas con cobertura"
    echo "  seed         - Generar datos de prueba"
    echo "  clean        - Limpiar datos de prueba"
    echo "  help         - Mostrar esta ayuda"
    echo ""
}

# Opción por defecto
OPTION=${1:-all}

case $OPTION in
    all)
        echo -e "${BLUE}Ejecutando todas las pruebas...${NC}"
        python manage.py test inventario -v 2
        ;;
    
    models)
        echo -e "${BLUE}Ejecutando pruebas de modelos...${NC}"
        python manage.py test inventario.tests -v 2
        ;;
    
    api)
        echo -e "${BLUE}Ejecutando pruebas de API...${NC}"
        python manage.py test inventario.test_api -v 2
        ;;
    
    movements)
        echo -e "${BLUE}Ejecutando pruebas de movimientos...${NC}"
        python manage.py test inventario.tests.MovimientoInventarioTests -v 2
        ;;
    
    coverage)
        echo -e "${BLUE}Ejecutando pruebas con cobertura...${NC}"
        coverage run --source='inventario' manage.py test inventario
        echo ""
        echo -e "${GREEN}Reporte de cobertura:${NC}"
        coverage report
        echo ""
        echo -e "${YELLOW}Generando reporte HTML en htmlcov/index.html${NC}"
        coverage html
        ;;
    
    seed)
        echo -e "${BLUE}Generando datos de prueba...${NC}"
        python manage.py seed_test_data
        ;;
    
    clean)
        echo -e "${BLUE}Limpiando base de datos...${NC}"
        python manage.py flush --no-input
        echo -e "${GREEN}Base de datos limpiada${NC}"
        ;;
    
    help)
        show_help
        ;;
    
    *)
        echo -e "${YELLOW}Opción no reconocida: $OPTION${NC}"
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Completado${NC}"
