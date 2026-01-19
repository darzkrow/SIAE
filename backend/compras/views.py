from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OrdenCompra, ItemOrden
from .serializers import OrdenCompraSerializer, ItemOrdenSerializer
from rest_framework.permissions import IsAuthenticated
from auditoria.mixins import AuditMixin, TrashBinMixin

class OrdenCompraViewSet(AuditMixin, TrashBinMixin, viewsets.ModelViewSet):
    queryset = OrdenCompra.objects.all()
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'solicitante']
    search_fields = ['codigo', 'notas']

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        orden = self.get_object()
        orden.status = 'SOLICITADO'
        orden.aprobador = request.user
        orden.save()
        return Response({'status': 'Orden aprobada/solicitada'})

class ItemOrdenViewSet(viewsets.ModelViewSet):
    queryset = ItemOrden.objects.all()
    serializer_class = ItemOrdenSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['orden']
