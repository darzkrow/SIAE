from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import CategoriaProducto, Marca
from .serializers import CategoriaProductoSerializer, MarcaSerializer
from rest_framework.permissions import IsAuthenticated
from auditoria.mixins import AuditMixin, TrashBinMixin

class CategoriaProductoViewSet(AuditMixin, TrashBinMixin, viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'codigo']

class MarcaViewSet(AuditMixin, TrashBinMixin, viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre']
