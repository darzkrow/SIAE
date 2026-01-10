"""
URLs para el sistema de inventario refactorizado.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from inventario import views

# Crear router para las nuevas rutas
router = DefaultRouter()

# Modelos auxiliares
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'units', views.UnitOfMeasureViewSet, basename='unit')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'acueductos', views.AcueductoViewSet, basename='acueducto')

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

# Alertas y Notificaciones
router.register(r'alertas', views.AlertaViewSet, basename='alerta')
router.register(r'notificaciones', views.NotificacionViewSet, basename='notificacion')

urlpatterns = [
    path('', include(router.urls)),
]
