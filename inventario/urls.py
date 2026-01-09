from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'organizaciones', views.OrganizacionCentralViewSet)
router.register(r'sucursales', views.SucursalViewSet)
router.register(r'acueductos', views.AcueductoViewSet)
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'tuberias', views.TuberiaViewSet)
router.register(r'equipos', views.EquipoViewSet)
router.register(r'stock-tuberias', views.StockTuberiaViewSet)
router.register(r'stock-equipos', views.StockEquipoViewSet)
router.register(r'movimientos', views.MovimientoInventarioViewSet)
router.register(r'audits', views.InventoryAuditViewSet)
router.register(r'reportes', views.ReportesViewSet, basename='reportes')
router.register(r'alertas', views.AlertaStockViewSet)
router.register(r'notificaciones', views.NotificationViewSet)
router.register(r'users', views.CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
