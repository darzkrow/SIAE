from rest_framework.routers import DefaultRouter
from activos.views import (
    MaterialEstrategicoViewSet, ActivoFijoViewSet,
    FichaTecnicaMotorViewSet, RegistroMantenimientoViewSet
)

router = DefaultRouter()
router.register(r'estrategicos', MaterialEstrategicoViewSet)
router.register(r'activos-fijos', ActivoFijoViewSet)
router.register(r'fichas-tecnicas', FichaTecnicaMotorViewSet)
router.register(r'mantenimientos', RegistroMantenimientoViewSet)

urlpatterns = router.urls
