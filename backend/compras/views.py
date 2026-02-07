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
            'aprobado_comercializacion_por',
            'aprobado_presupuesto_por',
            'aprobado_finanzas_por',
            'ejecutado_compras_por',
            'movimiento'
        ).prefetch_related('items__content_type')

    @action(detail=False, methods=['post'])
    def consolidar(self, request):
        """Consolidar múltiples órdenes individuales en una orden global"""
        from .serializers import ConsolidacionSerializer
        serializer = ConsolidacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ordenes_ids = serializer.validated_data['ordenes_ids']
        ordenes = OrdenCompra.objects.filter(id__in=ordenes_ids, tipo=OrdenCompra.Tipo.INDIVIDUAL, status__in=[OrdenCompra.Status.PENDIENTE_COMERCIALIZACION, OrdenCompra.Status.BORRADOR])
        
        if not ordenes.exists():
            return Response({'error': 'No se encontraron órdenes válidas para consolidar'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear Orden Global
        # La orden global no tiene items directos, es un contenedor
        orden_global = OrdenCompra.objects.create(
            tipo=OrdenCompra.Tipo.GLOBAL,
            solicitante=request.user,
            status=OrdenCompra.Status.PENDIENTE_COMERCIALIZACION,
            notas=f"Orden Global consolidada de {ordenes.count()} órdenes individuales."
        )

        # Asignar padre
        ordenes.update(parent_order=orden_global)
        
        return Response(OrdenCompraSerializer(orden_global).data)

    @action(detail=True, methods=['post'], url_path='aprobar-comercializacion')
    def aprobar_comercializacion(self, request, pk=None):
        orden = self.get_object()
        if orden.status != OrdenCompra.Status.PENDIENTE_COMERCIALIZACION:
             return Response({'error': 'Orden no está en estado pendiente comercialización'}, status=status.HTTP_400_BAD_REQUEST)
        
        orden.status = OrdenCompra.Status.PENDIENTE_PRESUPUESTO
        orden.aprobado_comercializacion_por = request.user
        from django.utils import timezone
        orden.fecha_aprobacion_comercializacion = timezone.now()
        orden.save()
        return Response({'status': 'Aprobado por Comercialización -> Pendiente Presupuesto'})

    @action(detail=True, methods=['post'], url_path='aprobar-presupuesto')
    def aprobar_presupuesto(self, request, pk=None):
        orden = self.get_object()
        if orden.status != OrdenCompra.Status.PENDIENTE_PRESUPUESTO:
             return Response({'error': 'Orden no está en estado pendiente presupuesto'}, status=status.HTTP_400_BAD_REQUEST)
        
        orden.status = OrdenCompra.Status.PENDIENTE_FINANZAS
        orden.aprobado_presupuesto_por = request.user
        from django.utils import timezone
        orden.fecha_aprobacion_presupuesto = timezone.now()
        orden.save()
        return Response({'status': 'Aprobado por Presupuesto -> Pendiente Finanzas'})

    @action(detail=True, methods=['post'], url_path='aprobar-finanzas')
    def aprobar_finanzas(self, request, pk=None):
        orden = self.get_object()
        if orden.status != OrdenCompra.Status.PENDIENTE_FINANZAS:
             return Response({'error': 'Orden no está en estado pendiente finanzas'}, status=status.HTTP_400_BAD_REQUEST)
        
        orden.status = OrdenCompra.Status.PENDIENTE_COMPRAS
        orden.aprobado_finanzas_por = request.user
        from django.utils import timezone
        orden.fecha_aprobacion_finanzas = timezone.now()
        orden.save()
        return Response({'status': 'Aprobado por Finanzas -> Pendiente Compras'})

    @action(detail=True, methods=['post'], url_path='ejecutar-compra')
    def ejecutar_compra(self, request, pk=None):
        orden = self.get_object()
        if orden.status != OrdenCompra.Status.PENDIENTE_COMPRAS:
             return Response({'error': 'Orden no está en estado pendiente compras'}, status=status.HTTP_400_BAD_REQUEST)
        
        orden.status = OrdenCompra.Status.COMPLETADO # O EN_PROCESO dependiendo del flujo real de recepción
        orden.ejecutado_compras_por = request.user
        from django.utils import timezone
        orden.fecha_ejecucion_compras = timezone.now()
        orden.save()
        return Response({'status': 'Ejecutado por Compras -> Completado'})

    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        orden = self.get_object()
        motivo = request.data.get('motivo')
        if not motivo:
            return Response({'error': 'Motivo requerido'}, status=status.HTTP_400_BAD_REQUEST)

        orden.status = OrdenCompra.Status.CANCELADO
        orden.motivo_cancelacion = motivo
        orden.save()
        return Response({'status': 'Orden Cancelada'})


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
