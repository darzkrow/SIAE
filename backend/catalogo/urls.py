from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoriaProductoViewSet, MarcaViewSet, TagViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
