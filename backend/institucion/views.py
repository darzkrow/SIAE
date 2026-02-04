"""
API Views for Hidroven Organizational Restructuring.
Provides both new hierarchical API endpoints and backward compatibility.
"""
from rest_framework import viewsets
from core.viewsets import BaseModelViewSet, SoftDeleteViewSet, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.contrib.auth import get_user_model
from auditoria.mixins import AuditMixin, TrashBinMixin

from .models import (
    # New hierarchical models
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado, AprobacionTraslado,
    MigracionOrganizacional,
    # Legacy models for backward compatibility
    OrganizacionCentral, Sucursal, Acueducto
)
from .serializers import (
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


class AlmacenRegionalViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for AlmacenRegional management."""
    
    queryset = AlmacenRegional.objects.all()
    serializer_class = AlmacenRegionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['unidad_organizacional', 'prefijo', 'activo', 'manager']
    search_fields = ['nombre', 'prefijo', 'ubicacion', 'descripcion']
    ordering_fields = ['nombre', 'prefijo', 'fecha_creacion']
    ordering = ['prefijo']


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


class SolicitudTrasladoViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for SolicitudTraslado management with dual approval workflow."""
    
    queryset = SolicitudTraslado.objects.all()
    serializer_class = SolicitudTrasladoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'prioridad', 'almacen_origen', 'almacen_destino', 'solicitante']
    search_fields = ['numero_solicitud', 'activo__codigo_actual', 'motivo']
    ordering_fields = ['fecha_solicitud', 'fecha_limite', 'prioridad']
    ordering = ['-fecha_solicitud']


class HistorialMovimientoActivoViewSet(BaseModelViewSet):
    """Read-only ViewSet for HistorialMovimientoActivo (immutable audit trail)."""
    
    queryset = HistorialMovimientoActivo.objects.all()
    serializer_class = HistorialMovimientoActivoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['activo', 'tipo_movimiento', 'almacen_origen', 'almacen_destino', 'usuario_responsable']
    search_fields = ['activo__codigo_actual', 'motivo', 'observaciones']
    ordering_fields = ['fecha_movimiento']
    ordering = ['-fecha_movimiento']


class MigracionOrganizacionalViewSet(BaseModelViewSet):
    """ViewSet for monitoring organizational migration status."""
    
    queryset = MigracionOrganizacional.objects.all()
    serializer_class = MigracionOrganizacionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado_migracion', 'validado', 'migrado_por']
    search_fields = ['notas']
    ordering_fields = ['fecha_migracion', 'fecha_validacion']
    ordering = ['-fecha_migracion']
    
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