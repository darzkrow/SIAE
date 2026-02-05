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
    MigracionOrganizacional,
    # Legacy models for backward compatibility
    OrganizacionCentral, Sucursal, Acueducto
)
from .serializers import (
    SubalmacenSerializer,
    # New hierarchical serializers
    EmpresaSerializer, VicepresidenciaSerializer, UnidadOrganizacionalSerializer,
    AlmacenRegionalSerializer, MigracionOrganizacionalSerializer,
    # Backward compatibility serializers
    OrganizacionCentralSerializer, SucursalSerializer, AcueductoSerializer,
    # Specialized serializers
    HierarchyTreeSerializer
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
        """Optimize queryset with prefetch_related for hierarchy."""
        return super().get_queryset().prefetch_related(
            'subsidiarias',
            'vicepresidencias'
        )


class VicepresidenciaViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for Vicepresidencia management."""
    
    queryset = Vicepresidencia.objects.all()
    serializer_class = VicepresidenciaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['empresa', 'tipo', 'activo']
    search_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo', 'empresa']
    ordering = ['empresa', 'nombre']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related('empresa', 'responsable').prefetch_related(
            'unidades_organizacionales'
        )


class UnidadOrganizacionalViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for UnidadOrganizacional management."""
    
    queryset = UnidadOrganizacional.objects.all()
    serializer_class = UnidadOrganizacionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vicepresidencia', 'tipo', 'activo']
    search_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo', 'vicepresidencia']
    ordering = ['vicepresidencia', 'nombre']
    
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
    filterset_fields = ['unidad_organizacional', 'activo']
    search_fields = ['nombre', 'prefijo']
    ordering_fields = ['nombre', 'prefijo', 'unidad_organizacional']
    ordering = ['unidad_organizacional', 'nombre']
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return super().get_queryset().select_related(
            'unidad_organizacional__vicepresidencia__empresa',
            'manager'
        )


class SubalmacenViewSet(AuditMixin, TrashBinMixin, SoftDeleteViewSet):
    """ViewSet for Subalmacén management (Inherited from original system)."""
    
    queryset = Subalmacen.objects.all()
    serializer_class = SubalmacenSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['sucursal', 'estado', 'activo']
    search_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo']


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


# ============================================================================
# BACKWARD COMPATIBILITY VIEWSETS
# ============================================================================

class OrganizacionCentralViewSet(SoftDeleteViewSet):
    """Backward compatibility ViewSet for OrganizacionCentral."""
    queryset = OrganizacionCentral.objects.all()
    serializer_class = OrganizacionCentralSerializer
    permission_classes = [permissions.IsAuthenticated]


class SucursalViewSet(SoftDeleteViewSet):
    """Backward compatibility ViewSet for Sucursal."""
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [permissions.IsAuthenticated]


class AcueductoViewSet(SoftDeleteViewSet):
    """Backward compatibility ViewSet for Acueducto."""
    queryset = Acueducto.objects.all()
    serializer_class = AcueductoSerializer
    permission_classes = [permissions.IsAuthenticated]