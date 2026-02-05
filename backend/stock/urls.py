from rest_framework.routers import DefaultRouter
from stock.views import StockViewSet, MovimientoInventarioViewSet, InventoryAuditViewSet, InventoryReportViewSet

router = DefaultRouter()
router.register(r'existencias', StockViewSet)
router.register(r'movimientos', MovimientoInventarioViewSet)
router.register(r'auditoria', InventoryAuditViewSet)
router.register(r'reportes-v2', InventoryReportViewSet, basename='reportes-v2')

urlpatterns = router.urls
