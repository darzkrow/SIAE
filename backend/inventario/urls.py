from rest_framework.routers import DefaultRouter
from django.urls import path, include
from productos.views import (
    UnitOfMeasureViewSet, ChemicalProductViewSet,
    PipeViewSet, PumpAndMotorViewSet, AccessoryViewSet
)
from proveedores.views import SupplierViewSet
from stock.views import (
    StockViewSet, MovimientoInventarioViewSet, 
    InventoryAuditViewSet, InventoryReportViewSet
)
from activos.views import (
    MaterialEstrategicoViewSet, ActivoFijoViewSet,
    FichaTecnicaMotorViewSet, RegistroMantenimientoViewSet
)
from institucion.views import (
    OrganizacionCentralViewSet, SucursalViewSet, AcueductoViewSet
)
from accounts.views import UserViewSet

# New router for the legacy 'api/' prefix
router = DefaultRouter()

# Auxiliares / Organizacionales
router.register(r'organizaciones', OrganizacionCentralViewSet, basename='organizacion')
router.register(r'sucursales', SucursalViewSet, basename='sucursal')
router.register(r'acueductos', AcueductoViewSet, basename='acueducto')
router.register(r'users', UserViewSet, basename='user')

# Auxiliares / Productos
router.register(r'units', UnitOfMeasureViewSet, basename='unit')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'chemicals', ChemicalProductViewSet, basename='chemical')
router.register(r'pipes', PipeViewSet, basename='pipe')
router.register(r'pumps', PumpAndMotorViewSet, basename='pump')
router.register(r'accessories', AccessoryViewSet, basename='accessory')

# Stock / Movimientos
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento')
router.register(r'auditoria', InventoryAuditViewSet, basename='auditoria')

# Reportes
router.register(r'reportes-v2', InventoryReportViewSet, basename='reportes-v2')

# Gestión Estratégica / Activos
router.register(r'materiales-estrategicos', MaterialEstrategicoViewSet, basename='material-estrategico')
router.register(r'activos-fijos', ActivoFijoViewSet, basename='activo-fijo')
router.register(r'fichas-tecnicas', FichaTecnicaMotorViewSet, basename='ficha-tecnica')
router.register(r'mantenimientos', RegistroMantenimientoViewSet, basename='mantenimiento')

urlpatterns = [
    path('', include(router.urls)),
]
