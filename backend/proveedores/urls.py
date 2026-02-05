from django.urls import path, include
from rest_framework.routers import DefaultRouter
from proveedores.views import SupplierViewSet

router = DefaultRouter()
router.register(r'', SupplierViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
