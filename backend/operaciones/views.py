"""
API Views for Operaciones App.
Handles asset tracking, transfer workflows, and audit trails.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.viewsets import BaseModelViewSet, SoftDeleteViewSet
from auditoria.mixins import AuditMixin, TrashBinMixin

from .models import (
    ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado, AprobacionTraslado,
    AuditoriaEstadoActivo, AuditoriaAprobacion, AuditoriaOperacionSistema, AuditoriaAccesoSistema
)
from .serializers import (
    ActivoInventarioSerializer, HistorialMovimientoActivoSerializer,
    SolicitudTrasladoSerializer, AprobacionTrasladoSerializer,
    AssetTrackingSerializer,
    AuditoriaEstadoActivoSerializer, AuditoriaAprobacionSerializer,
    AuditoriaOperacionSistemaSerializer, AuditoriaAccesoSistemaSerializer
)

User = get_user_model()


class ActivoInventarioViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for ActivoInventario management."""
    
    queryset = ActivoInventario.objects.all()
    serializer_class = ActivoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'tipo_activo', 'almacen_actual', 'fecha_ingreso']
    search_fields = ['codigo_actual', 'codigo_original', 'descripcion', 'numero_serie']
    ordering_fields = ['fecha_ingreso', 'valor_unitario', 'codigo_actual']
    ordering = ['-fecha_ingreso']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'almacen_actual',
            'almacen_actual__unidad_organizacional',
            'almacen_actual__unidad_organizacional__vicepresidencia'
        ).prefetch_related('historial_movimientos')
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Get detailed asset tracking information."""
        asset = self.get_object()
        serializer = AssetTrackingSerializer(asset)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='change-state')
    def change_state(self, request, pk=None):
        """Change asset state with validation and audit."""
        asset = self.get_object()
        new_state = request.data.get('estado')
        motivo = request.data.get('motivo', 'Manual state change')
        observaciones = request.data.get('observaciones', '')
        
        if not new_state:
            return Response({'error': 'State is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        success = asset.change_state(
            new_state=new_state,
            user=request.user,
            motivo=motivo,
            observaciones=observaciones
        )
        
        if success:
            return Response({'message': f'State changed to {new_state}'})
        return Response({'error': 'Invalid state transition'}, status=status.HTTP_400_BAD_REQUEST)


class SolicitudTrasladoViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for SolicitudTraslado management with dual approval workflow."""
    
    queryset = SolicitudTraslado.objects.all()
    serializer_class = SolicitudTrasladoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'prioridad', 'almacen_origen', 'almacen_destino', 'solicitante']
    search_fields = ['numero_solicitud', 'activo__codigo_actual', 'motivo']
    ordering_fields = ['fecha_solicitud', 'fecha_limite', 'prioridad']
    ordering = ['-fecha_solicitud']
    
    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset().select_related(
            'activo',
            'almacen_origen',
            'almacen_destino',
            'solicitante',
            'ejecutor'
        ).prefetch_related('aprobaciones')
    
    @action(detail=True, methods=['post'], url_path='aprobar-origen')
    def aprobar_origen(self, request, pk=None):
        """Aprobar solicitud desde almacén de origen."""
        solicitud = self.get_object()
        
        # Check permissions (simplified for now, model handles core logic)
        if solicitud.almacen_origen.manager != request.user and not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            aprobacion = AprobacionTraslado.objects.create(
                solicitud=solicitud,
                aprobador=request.user,
                tipo_aprobacion='ORIGEN',
                decision='APROBADO',
                comentarios=request.data.get('comentarios', '')
            )
            return Response({'message': 'Approved by origin'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'], url_path='aprobar-destino')
    def aprobar_destino(self, request, pk=None):
        """Aprobar solicitud desde almacén de destino."""
        solicitud = self.get_object()
        
        if solicitud.almacen_destino.manager != request.user and not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            aprobacion = AprobacionTraslado.objects.create(
                solicitud=solicitud,
                aprobador=request.user,
                tipo_aprobacion='DESTINO',
                decision='APROBADO',
                comentarios=request.data.get('comentarios', '')
            )
            return Response({'message': 'Approved by destination'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='execute')
    def execute_transfer(self, request, pk=None):
        """Execute the physical transfer."""
        solicitud = self.get_object()
        try:
            solicitud.execute_transfer(request.user)
            return Response({'message': 'Transfer executed successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'], url_path='complete')
    def complete_transfer(self, request, pk=None):
        """Complete the transfer on arrival."""
        solicitud = self.get_object()
        try:
            solicitud.complete_transfer(request.user)
            return Response({'message': 'Transfer completed successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HistorialMovimientoActivoViewSet(BaseModelViewSet):
    """Read-only ViewSet for HistorialMovimientoActivo (immutable audit trail)."""
    
    queryset = HistorialMovimientoActivo.objects.all()
    serializer_class = HistorialMovimientoActivoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activo', 'tipo_movimiento', 'almacen_origen', 'almacen_destino', 'usuario_responsable']
    search_fields = ['activo__codigo_actual', 'motivo', 'observaciones']
    ordering_fields = ['fecha_movimiento']
    ordering = ['-fecha_movimiento']


class AuditoriaEstadoActivoViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet for asset state audit trail."""
    queryset = AuditoriaEstadoActivo.objects.all()
    serializer_class = AuditoriaEstadoActivoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activo', 'estado_nuevo', 'exitoso']

class AuditoriaAprobacionViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet for approval audit trail."""
    queryset = AuditoriaAprobacion.objects.all()
    serializer_class = AuditoriaAprobacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['solicitud_traslado', 'accion']

class AuditoriaOperacionSistemaViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet for systemic operation audit trail."""
    queryset = AuditoriaOperacionSistema.objects.all()
    serializer_class = AuditoriaOperacionSistemaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['accion', 'exitosa']

class AuditoriaAccesoSistemaViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet for access audit trail."""
    queryset = AuditoriaAccesoSistema.objects.all()
    serializer_class = AuditoriaAccesoSistemaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['accion', 'exitoso', 'nivel_riesgo']
