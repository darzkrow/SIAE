"""
URLs para el sistema de inventario refactorizado.
Agregar estas rutas a inventario/urls.py después de la migración.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

# TODO: Descomentar después de la migración
# from inventario.views_refactored import (
#     CategoryViewSet, UnitOfMeasureViewSet, SupplierViewSet,
#     ChemicalProductViewSet, PipeViewSet,
#     PumpAndMotorViewSet, AccessoryViewSet,
#     StockChemicalViewSet, StockPipeViewSet,
#     StockPumpAndMotorViewSet, StockAccessoryViewSet,
#     RefactoredReportesViewSet
# )

# Crear router para las nuevas rutas
router_refactored = DefaultRouter()

# Modelos auxiliares
# router_refactored.register(r'categories', CategoryViewSet, basename='category')
# router_refactored.register(r'units', UnitOfMeasureViewSet, basename='unit')
# router_refactored.register(r'suppliers', SupplierViewSet, basename='supplier')

# Productos
# router_refactored.register(r'chemicals', ChemicalProductViewSet, basename='chemical')
# router_refactored.register(r'pipes', PipeViewSet, basename='pipe')
# router_refactored.register(r'pumps', PumpAndMotorViewSet, basename='pump')
# router_refactored.register(r'accessories', AccessoryViewSet, basename='accessory')

# Stock
# router_refactored.register(r'stock-chemicals', StockChemicalViewSet, basename='stock-chemical')
# router_refactored.register(r'stock-pipes', StockPipeViewSet, basename='stock-pipe')
# router_refactored.register(r'stock-pumps', StockPumpAndMotorViewSet, basename='stock-pump')
# router_refactored.register(r'stock-accessories', StockAccessoryViewSet, basename='stock-accessory')

# Reportes
# router_refactored.register(r'reportes-v2', RefactoredReportesViewSet, basename='reportes-v2')

# URLs patterns
# Agregar esto a inventario/urls.py:
# urlpatterns = [
#     ... rutas existentes ...
#     path('api/v2/', include(router_refactored.urls)),
# ]

"""
EJEMPLO DE ENDPOINTS DISPONIBLES DESPUÉS DE LA MIGRACIÓN:

Modelos Auxiliares:
- GET/POST /api/v2/categories/
- GET/PUT/DELETE /api/v2/categories/{id}/
- GET/POST /api/v2/units/
- GET/POST /api/v2/suppliers/

Productos Químicos:
- GET/POST /api/v2/chemicals/
- GET/PUT/DELETE /api/v2/chemicals/{id}/
- GET /api/v2/chemicals/stock_bajo/
- GET /api/v2/chemicals/peligrosos/
- GET /api/v2/chemicals/proximos_vencer/

Tuberías:
- GET/POST /api/v2/pipes/
- GET/PUT/DELETE /api/v2/pipes/{id}/
- GET /api/v2/pipes/by_diameter/?diametro=110

Bombas y Motores:
- GET/POST /api/v2/pumps/
- GET/PUT/DELETE /api/v2/pumps/{id}/
- GET /api/v2/pumps/by_power_range/?min_hp=5&max_hp=10

Accesorios:
- GET/POST /api/v2/accessories/
- GET/PUT/DELETE /api/v2/accessories/{id}/
- GET /api/v2/accessories/valvulas/

Stock:
- GET/POST /api/v2/stock-chemicals/
- GET/POST /api/v2/stock-pipes/
- GET/POST /api/v2/stock-pumps/
- GET/POST /api/v2/stock-accessories/

Reportes:
- GET /api/v2/reportes-v2/dashboard_stats/
- GET /api/v2/reportes-v2/stock_por_categoria/
- GET /api/v2/reportes-v2/valor_inventario_por_tipo/
"""
