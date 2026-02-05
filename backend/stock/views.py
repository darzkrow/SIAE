from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, F, Count
from core.viewsets import BaseAPIViewSet
from stock.models import Stock, MovimientoInventario, InventoryAudit
from activos.models import MaterialEstrategico, ActivoFijo
from stock.serializers import StockSerializer, MovimientoInventarioSerializer, InventoryAuditSerializer
from stock.filters import MovimientoInventarioFilter

class StockViewSet(BaseAPIViewSet):
    queryset = Stock.objects.select_related('ubicacion').all()
    serializer_class = StockSerializer
    filterset_fields = ['ubicacion', 'estado_operativo']
    search_fields = ['lote']

class MovimientoInventarioViewSet(BaseAPIViewSet):
    queryset = MovimientoInventario.objects.select_related('ubicacion_origen', 'ubicacion_destino').all()
    serializer_class = MovimientoInventarioSerializer
    filterset_class = MovimientoInventarioFilter
    search_fields = ['razon']

class InventoryAuditViewSet(BaseAPIViewSet):
    queryset = InventoryAudit.objects.all()
    serializer_class = InventoryAuditSerializer
    filterset_fields = ['status', 'tipo_movimiento']
    search_fields = ['mensaje']

class InventoryReportViewSet(BaseAPIViewSet):
    """ViewSet para reportes consolidados del inventario."""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Estadísticas generales para el dashboard."""
        try:
            total_quimicos = Stock.objects.filter(content_type__model='chemicalproduct').count()
            total_tuberias = Stock.objects.filter(content_type__model='pipe').count()
            total_equipos = Stock.objects.filter(content_type__model='pumpandmotor').count()
            
            # Note: We skip the complex date filtering for now to ensure stability
            return Response({
                'total_quimicos': total_quimicos,
                'total_tuberias': total_tuberias,
                'total_equipos': total_equipos,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def resumen_movimientos(self, request):
        """Resumen de movimientos por tipo."""
        resumen = MovimientoInventario.objects.values('tipo_movimiento').annotate(
            total=Count('id'),
            cantidad_total=Sum('cantidad')
        )
        return Response(list(resumen))
