from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StateViewSet, MunicipalityViewSet, ParishViewSet

router = DefaultRouter()
router.register('states', StateViewSet, basename='states')
router.register('municipalities', MunicipalityViewSet, basename='municipalities')
router.register('parishes', ParishViewSet, basename='parishes')

from .views import UbicacionViewSet
router.register('ubicaciones', UbicacionViewSet, basename='ubicaciones')

urlpatterns = [
    path('', include(router.urls)),
]
