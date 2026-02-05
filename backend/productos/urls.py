from rest_framework.routers import DefaultRouter
from productos.views import (
    UnitOfMeasureViewSet,
    ChemicalProductViewSet, PipeViewSet,
    PumpAndMotorViewSet, AccessoryViewSet
)

router = DefaultRouter()
router.register(r'unidades', UnitOfMeasureViewSet)
# proveedores movido a aplicación dedicada
router.register(r'quimicos', ChemicalProductViewSet)
router.register(r'tuberias', PipeViewSet)
router.register(r'equipos', PumpAndMotorViewSet)
router.register(r'accesorios', AccessoryViewSet)

urlpatterns = router.urls
