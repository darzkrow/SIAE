from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrdenCompraViewSet, ItemOrdenViewSet

router = DefaultRouter()
router.register(r'ordenes', OrdenCompraViewSet)
router.register(r'items', ItemOrdenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
