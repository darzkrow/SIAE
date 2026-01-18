"""
URLs para el sistema de inventario refactorizado.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from inventario import views
from inventario.views_import import CSVImportViewSet

# Crear router para las nuevas rutas
router = DefaultRouter()

# Modelos auxiliares
router.register(r'organizaciones', views.OrganizacionCentralViewSet, basename='organizacion')
router.register(r'sucursales', views.SucursalViewSet, basename='sucursal')
router.register(r'units', views.UnitOfMeasureViewSet, basename='unit')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'acueductos', views.AcueductoViewSet, basename='acueducto')
router.register(r'users', views.UserViewSet, basename='user')

# Productos
router.register(r'chemicals', views.ChemicalProductViewSet, basename='chemical')
router.register(r'pipes', views.PipeViewSet, basename='pipe')
router.register(r'pumps', views.PumpAndMotorViewSet, basename='pump')
router.register(r'accessories', views.AccessoryViewSet, basename='accessory')

# Stock
router.register(r'stock-chemicals', views.StockChemicalViewSet, basename='stock-chemical')
router.register(r'stock-pipes', views.StockPipeViewSet, basename='stock-pipe')
router.register(r'stock-pumps', views.StockPumpAndMotorViewSet, basename='stock-pump')
router.register(r'stock-accessories', views.StockAccessoryViewSet, basename='stock-accessory')

# Movimientos
router.register(r'movimientos', views.MovimientoInventarioViewSet, basename='movimiento')

# Reportes
router.register(r'reportes-v2', views.RefactoredReportesViewSet, basename='reportes-v2')

# Mantenimiento
router.register(r'fichas-tecnicas', views.FichaTecnicaMotorViewSet, basename='ficha-tecnica')
router.register(r'mantenimientos', views.RegistroMantenimientoViewSet, basename='mantenimiento')

# Importación
router.register(r'import', CSVImportViewSet, basename='import')

urlpatterns = [
    path('', include(router.urls)),
]
