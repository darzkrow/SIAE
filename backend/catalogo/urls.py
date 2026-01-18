from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoriaProductoViewSet, MarcaViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'marcas', MarcaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
