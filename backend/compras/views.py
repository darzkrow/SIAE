from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.viewsets import SoftDeleteViewSet, BaseModelViewSet
from .models import OrdenCompra, ItemOrden
from .serializers import OrdenCompraSerializer, ItemOrdenSerializer
from rest_framework.permissions import IsAuthenticated
from auditoria.mixins import AuditMixin, TrashBinMixin


class OrdenCompraViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet para órdenes de compra con soft delete"""
    queryset = OrdenCompra.objects.all()
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'solicitante']
    search_fields = ['codigo', 'notas']
    
    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset().select_related(
            'solicitante',
            'aprobador',
            'movimiento'
        ).prefetch_related('items__content_type')

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        orden = self.get_object()
        orden.status = 'SOLICITADO'
        orden.aprobador = request.user
        orden.save()
        return Response({'status': 'Orden aprobada/solicitada'})


class ItemOrdenViewSet(BaseModelViewSet):
    """ViewSet para items de orden"""
    queryset = ItemOrden.objects.all()
    serializer_class = ItemOrdenSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['orden']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'orden__solicitante',
            'content_type'
        )
