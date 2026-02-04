"""
API Views for Hidroven Organizational Restructuring.
Provides both new hierarchical API endpoints and backward compatibility.
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
    Subalmacen,
    # New hierarchical models
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado, AprobacionTraslado,
    MigracionOrganizacional,
    # Legacy models for backward compatibility
    OrganizacionCentral, Sucursal, Acueducto
)
from .serializers import (
    SubalmacenSerializer,
    # New hierarchical serializers
    EmpresaSerializer, VicepresidenciaSerializer, UnidadOrganizacionalSerializer,
    AlmacenRegionalSerializer, ActivoInventarioSerializer, HistorialMovimientoActivoSerializer,
    SolicitudTrasladoSerializer, AprobacionTrasladoSerializer, MigracionOrganizacionalSerializer,
    # Backward compatibility serializers
    OrganizacionCentralSerializer, SucursalSerializer, AcueductoSerializer,
    # Specialized serializers
    AssetTrackingSerializer, TransferWorkflowSerializer, HierarchyTreeSerializer
)

User = get_user_model()


# ============================================================================
# NEW HIERARCHICAL API VIEWSETS
# ============================================================================

class EmpresaViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for Empresa (root company) management."""
    
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activo', 'codigo']
    search_fields = ['nombre', 'codigo', 'rif']
    ordering_fields = ['nombre', 'codigo', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_queryset(self):
        """Optimize queryset with prefetch_related."""
        return super().get_queryset().prefetch_related(
            'subsidiarias', 'vicepresidencias'
        )
    
    @action(detail=True, methods=['get'])
    def hierarchy_tree(self, request, pk=None):
        """Get complete hierarchy tree for this empresa."""
        empresa = self.get_object()
        serializer = HierarchyTreeSerializer(empresa, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def vicepresidencias(self, request, pk=None):
        """Get all vicepresidencias under this empresa."""
        empresa = self.get_object()
        vicepresidencias = empresa.vicepresidencias.filter(activo=True)
        serializer = VicepresidenciaSerializer(vicepresidencias, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def migration_status(self, request):
        """Get migration status for organizational restructuring."""
        from .services import MigrationEngine
        
        status_info = MigrationEngine.get_migration_status()
        return Response(status_info)


class VicepresidenciaViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for Vicepresidencia management."""
    
    queryset = Vicepresidencia.objects.all()
    serializer_class = VicepresidenciaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['empresa', 'tipo', 'activo']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'tipo', 'fecha_creacion']
    ordering = ['empresa', 'tipo', 'nombre']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'empresa', 'responsable'
        ).prefetch_related('unidades_organizacionales')


class UnidadOrganizacionalViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for UnidadOrganizacional management."""
    
    queryset = UnidadOrganizacional.objects.all()
    serializer_class = UnidadOrganizacionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vicepresidencia', 'tipo', 'activo']
    search_fields = ['nombre', 'codigo', 'descripcion', 'ubicacion']
    ordering_fields = ['nombre', 'tipo', 'fecha_creacion']
    ordering = ['vicepresidencia', 'tipo', 'nombre']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'vicepresidencia__empresa',
            'responsable'
        ).prefetch_related('almacenes_regionales')


class AlmacenRegionalViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for AlmacenRegional management."""
    
    queryset = AlmacenRegional.objects.all()
    serializer_class = AlmacenRegionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['unidad_organizacional', 'prefijo', 'activo', 'manager']
    search_fields = ['nombre', 'prefijo', 'ubicacion', 'descripcion']
    ordering_fields = ['nombre', 'prefijo', 'fecha_creacion']
    ordering = ['prefijo']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'unidad_organizacional__vicepresidencia__empresa',
            'manager'
        )


# ============================================================================
# BACKWARD COMPATIBILITY VIEWSETS
# ============================================================================

class OrganizacionCentralViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """Backward compatibility ViewSet for OrganizacionCentral."""
    
    queryset = OrganizacionCentral.objects.all()
    serializer_class = OrganizacionCentralSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['parent']
    search_fields = ['nombre', 'rif']
    ordering_fields = ['nombre']
    ordering = ['nombre']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related('parent').prefetch_related('sucursales')


class SucursalViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """Backward compatibility ViewSet for Sucursal."""
    
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['organizacion_central']
    search_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo']
    ordering = ['organizacion_central', 'nombre']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related('organizacion_central').prefetch_related('acueductos')


class AcueductoViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """Backward compatibility ViewSet for Acueducto."""
    
    queryset = Acueducto.objects.all()
    serializer_class = AcueductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['sucursal']
    search_fields = ['nombre', 'codigo', 'ubicacion']
    ordering_fields = ['nombre', 'codigo']
    ordering = ['sucursal', 'nombre']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related('sucursal__organizacion_central')


class ActivoInventarioViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for ActivoInventario management with asset tracking."""
    
    queryset = ActivoInventario.objects.all()
    serializer_class = ActivoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['almacen_actual', 'tipo_activo', 'estado']
    search_fields = ['codigo_actual', 'codigo_original', 'descripcion', 'numero_serie']
    ordering_fields = ['codigo_actual', 'fecha_ingreso', 'valor_unitario']
    ordering = ['-fecha_ingreso']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'tipo_activo',
            'almacen_actual__unidad_organizacional',
            'unidad_organizacional__vicepresidencia'
        ).prefetch_related('movimientos')


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
            'activo__tipo_activo',
            'almacen_origen__unidad_organizacional',
            'almacen_destino__unidad_organizacional',
            'solicitante'
        ).prefetch_related('aprobaciones')



    
    @action(detail=True, methods=['post'], url_path='aprobar-origen')
    def aprobar_origen(self, request, pk=None):
        """
        Aprobar solicitud desde almacén de origen.
        Puede ser llamado escaneando el QR code.
        """
        solicitud = self.get_object()
        
        # Validar que el usuario es responsable del almacén origen
        if not solicitud.almacen_origen.manager or solicitud.almacen_origen.manager != request.user:
            if not request.user.is_staff:
                return Response(
                    {'error': 'No tiene permisos para aprobar desde este almacén'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar estado
        if solicitud.estado != 'PENDIENTE':
            return Response(
                {'error': f'Solicitud en estado {solicitud.estado}, no se puede aprobar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear aprobación
        from .models import AprobacionTraslado
        aprobacion = AprobacionTraslado.objects.create(
            solicitud=solicitud,
            tipo_aprobacion='ORIGEN',
            aprobador=request.user,
            decision='APROBADO',
            comentarios=request.data.get('comentarios', '')
        )
        
        # Actualizar solicitud
        solicitud.aprobacion_origen = aprobacion
        solicitud.estado = 'APROBADA_ORIGEN'
        solicitud.save()
        
        return Response({
            'message': 'Solicitud aprobada por origen',
            'estado': solicitud.estado,
            'siguiente_paso': 'Esperando aprobación de destino'
        })
    
    @action(detail=True, methods=['post'], url_path='aprobar-destino')
    def aprobar_destino(self, request, pk=None):
        """
        Aprobar solicitud desde almacén de destino.
        Puede ser llamado escaneando el QR code.
        """
        solicitud = self.get_object()
        
        # Validar que el usuario es responsable del almacén destino
        if not solicitud.almacen_destino.manager or solicitud.almacen_destino.manager != request.user:
            if not request.user.is_staff:
                return Response(
                    {'error': 'No tiene permisos para aprobar desde este almacén'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar estado
        if solicitud.estado != 'APROBADA_ORIGEN':
            return Response(
                {'error': 'Solicitud debe estar aprobada por origen primero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear aprobación
        from .models import AprobacionTraslado
        aprobacion = AprobacionTraslado.objects.create(
            solicitud=solicitud,
            tipo_aprobacion='DESTINO',
            aprobador=request.user,
            decision='APROBADO',
            comentarios=request.data.get('comentarios', '')
        )
        
        # Actualizar solicitud
        solicitud.aprobacion_destino = aprobacion
        solicitud.estado = 'APROBADA_COMPLETA'
        solicitud.save()
        
        # Ejecutar traslado automáticamente
        try:
            solicitud.ejecutar_traslado(request.user)
        except Exception as e:
            return Response(
                {'error': f'Error al ejecutar traslado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Solicitud completamente aprobada y ejecutada',
            'estado': solicitud.estado,
        })
    
    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        """Rechazar solicitud de traslado"""
        solicitud = self.get_object()
        
        # Validar permisos
        if not request.user.is_staff:
            if solicitud.almacen_origen.manager != request.user and solicitud.almacen_destino.manager != request.user:
                return Response(
                    {'error': 'No tiene permisos para rechazar esta solicitud'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar estado
        if solicitud.estado not in ['PENDIENTE', 'APROBADA_ORIGEN']:
            return Response(
                {'error': f'No se puede rechazar solicitud en estado {solicitud.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado
        solicitud.estado = 'RECHAZADA'
        solicitud.observaciones += f"\n[{timezone.now()}] Rechazada por {request.user.username}: {request.data.get('motivo', 'Sin motivo')}"
        solicitud.save()
        
        return Response({
            'message': 'Solicitud rechazada',
            'estado': solicitud.estado,
        })
    
    @action(detail=True, methods=['get'], url_path='qr-code')
    def obtener_qr(self, request, pk=None):
        """Obtener o regenerar el QR code de la solicitud"""
        solicitud = self.get_object()
        
        if not solicitud.qr_code:
            solicitud.generar_qr_code(request)
        
        return Response({
            'qr_url': request.build_absolute_uri(solicitud.qr_code.url) if solicitud.qr_code else None,
            'approval_url': solicitud.qr_url,
            'numero_solicitud': solicitud.numero_solicitud,
            'estado': solicitud.estado,
        })


class HistorialMovimientoActivoViewSet(BaseModelViewSet):
    """Read-only ViewSet for HistorialMovimientoActivo (immutable audit trail)."""
    
    queryset = HistorialMovimientoActivo.objects.all()
    serializer_class = HistorialMovimientoActivoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activo', 'tipo_movimiento', 'almacen_origen', 'almacen_destino', 'usuario_responsable']
    search_fields = ['activo__codigo_actual', 'motivo', 'observaciones']
    ordering_fields = ['fecha_movimiento']
    ordering = ['-fecha_movimiento']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'activo__tipo_activo',
            'almacen_origen',
            'almacen_destino',
            'usuario_responsable',
            'solicitud_traslado'
        )


class MigracionOrganizacionalViewSet(BaseModelViewSet):
    """ViewSet for monitoring organizational migration status."""
    
    queryset = MigracionOrganizacional.objects.all()
    serializer_class = MigracionOrganizacionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado_migracion', 'validado', 'migrado_por']
    search_fields = ['notas']
    ordering_fields = ['fecha_migracion', 'fecha_validacion']
    ordering = ['-fecha_migracion']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'empresa',
            'vicepresidencia__empresa',
            'unidad_organizacional__vicepresidencia',
            'migrado_por',
            'validado_por',
            'revertido_por'
        )
    
    @action(detail=False, methods=['get'])
    def integrity_report(self, request):
        """Get migration integrity validation report."""
        integrity_result = MigracionOrganizacional.validar_integridad_migracion()
        return Response(integrity_result)
    
    @action(detail=False, methods=['get'])
    def summary_stats(self, request):
        """Get migration summary statistics."""
        total = self.get_queryset().count()
        completed = self.get_queryset().filter(estado_migracion='COMPLETADA').count()
        pending = self.get_queryset().filter(estado_migracion='PENDIENTE').count()
        failed = self.get_queryset().filter(estado_migracion='FALLIDA').count()
        validated = self.get_queryset().filter(validado=True).count()
        
        return Response({
            'total_migrations': total,
            'completed': completed,
            'pending': pending,
            'failed': failed,
            'validated': validated,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'validation_rate': (validated / completed * 100) if completed > 0 else 0
        })