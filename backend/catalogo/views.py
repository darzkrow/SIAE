from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.viewsets import SoftDeleteViewSet
from .models import CategoriaProducto, Marca, Tag
from .serializers import CategoriaProductoSerializer, MarcaSerializer, TagSerializer
from rest_framework.permissions import IsAuthenticated
from auditoria.mixins import AuditMixin, TrashBinMixin


class CategoriaProductoViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet para categorías de productos con soft delete"""
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'codigo']


class MarcaViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet para marcas con soft delete"""
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre']


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet para tags de productos"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
