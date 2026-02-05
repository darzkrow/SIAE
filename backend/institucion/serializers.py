"""
Serializers for Hidroven Organizational Restructuring API.
Provides both new hierarchical API endpoints and backward compatibility.
"""
from rest_framework import serializers
from core.serializers import BaseModelSerializer, SoftDeleteSerializer
from django.contrib.auth import get_user_model
from .models import (
    Subalmacen,
    # New hierarchical models
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado, AprobacionTraslado,
    MigracionOrganizacional,
    # Legacy models for backward compatibility
    OrganizacionCentral, Sucursal, Acueducto
)

User = get_user_model()

from .subalmacen_serializer import SubalmacenSerializer


# ============================================================================
# NEW HIERARCHICAL API SERIALIZERS
# ============================================================================

class EmpresaSerializer(BaseModelSerializer):
    """Serializer for Empresa (root company) model."""
    
    subsidiarias_count = serializers.SerializerMethodField()
    vicepresidencias_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Empresa
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'codigo', 'rif', 'direccion', 'telefono', 'email',
            'activo', 'fecha_creacion', 'fecha_actualizacion', 'parent',
            'subsidiarias_count', 'vicepresidencias_count', 'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_subsidiarias_count(self, obj):
        """Get count of subsidiary companies."""
        return obj.subsidiarias.count()
    
    def get_vicepresidencias_count(self, obj):
        """Get count of vicepresidencias under this company."""
        return obj.vicepresidencias.count()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


class VicepresidenciaSerializer(BaseModelSerializer):
    """Serializer for Vicepresidencia model."""
    
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    responsable_username = serializers.CharField(source='responsable.username', read_only=True)
    unidades_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Vicepresidencia
        fields = BaseModelSerializer.Meta.fields + [
            'empresa', 'empresa_nombre', 'nombre', 'codigo', 'tipo',
            'descripcion', 'responsable', 'responsable_username', 'activo',
            'fecha_creacion', 'fecha_actualizacion', 'parent',
            'unidades_count', 'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_unidades_count(self, obj):
        """Get count of organizational units under this VP."""
        return obj.unidades_organizacionales.count()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


class UnidadOrganizacionalSerializer(BaseModelSerializer):
    """Serializer for UnidadOrganizacional model."""
    
    vicepresidencia_nombre = serializers.CharField(source='vicepresidencia.nombre', read_only=True)
    empresa_nombre = serializers.CharField(source='vicepresidencia.empresa.nombre', read_only=True)
    responsable_username = serializers.CharField(source='responsable.username', read_only=True)
    almacenes_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = UnidadOrganizacional
        fields = BaseModelSerializer.Meta.fields + [
            'vicepresidencia', 'vicepresidencia_nombre', 'empresa_nombre',
            'nombre', 'codigo', 'tipo', 'descripcion', 'ubicacion',
            'responsable', 'responsable_username', 'activo',
            'fecha_creacion', 'fecha_actualizacion', 'parent',
            'almacenes_count', 'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_almacenes_count(self, obj):
        """Get count of regional warehouses under this unit."""
        return obj.almacenes_regionales.count()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


class AlmacenRegionalSerializer(BaseModelSerializer):
    """Serializer for AlmacenRegional model."""
    
    unidad_nombre = serializers.CharField(source='unidad_organizacional.nombre', read_only=True)
    vicepresidencia_nombre = serializers.CharField(source='unidad_organizacional.vicepresidencia.nombre', read_only=True)
    manager_username = serializers.CharField(source='manager.username', read_only=True)
    activos_count = serializers.SerializerMethodField()
    capacity_usage = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = AlmacenRegional
        fields = BaseModelSerializer.Meta.fields + [
            'unidad_organizacional', 'unidad_nombre', 'vicepresidencia_nombre',
            'nombre', 'prefijo', 'ubicacion', 'manager', 'manager_username',
            'capacidad_maxima', 'activo', 'fecha_creacion', 'fecha_actualizacion',
            'descripcion', 'telefono', 'email', 'activos_count', 'capacity_usage',
            'full_path'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_creacion', 'fecha_actualizacion']
    
    def get_activos_count(self, obj):
        """Get count of assets currently in this warehouse."""
        return obj.activos_actuales.count()
    
    def get_capacity_usage(self, obj):
        """Get current capacity usage percentage."""
        return obj.get_current_capacity_usage()
    
    def get_full_path(self, obj):
        """Get full hierarchical path."""
        return obj.get_full_path()


class ActivoInventarioSerializer(BaseModelSerializer):
    """Serializer for ActivoInventario model."""
    
    almacen_nombre = serializers.CharField(source='almacen_actual.nombre', read_only=True)
    almacen_prefijo = serializers.CharField(source='almacen_actual.prefijo', read_only=True)
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    movement_history = serializers.SerializerMethodField()
    transfer_count = serializers.SerializerMethodField()
    asset_age_days = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = ActivoInventario
        fields = BaseModelSerializer.Meta.fields + [
            'codigo_actual', 'codigo_original', 'tipo_activo', 'descripcion',
            'almacen_actual', 'almacen_nombre', 'almacen_prefijo', 'estado',
            'fecha_ingreso', 'valor_unitario', 'numero_serie',
            'producto_inventario_type', 'producto_inventario_id',
            'fecha_actualizacion', 'creado_por', 'creado_por_username',
            'actualizado_por', 'movement_history', 'transfer_count', 'asset_age_days'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'codigo_actual', 'codigo_original', 'fecha_ingreso', 'fecha_actualizacion',
            'movement_history', 'transfer_count', 'asset_age_days'
        ]
    
    def get_movement_history(self, obj):
        """Get movement history from asset code."""
        return obj.get_movement_history_from_code()
    
    def get_transfer_count(self, obj):
        """Get number of transfers from code evolution."""
        return obj.get_transfer_count()
    
    def get_asset_age_days(self, obj):
        """Get asset age in days."""
        return obj.get_asset_age_days()


class HistorialMovimientoActivoSerializer(BaseModelSerializer):
    """Serializer for HistorialMovimientoActivo model."""
    
    activo_codigo = serializers.CharField(source='activo.codigo_actual', read_only=True)
    almacen_origen_prefijo = serializers.CharField(source='almacen_origen.prefijo', read_only=True)
    almacen_destino_prefijo = serializers.CharField(source='almacen_destino.prefijo', read_only=True)
    usuario_username = serializers.CharField(source='usuario_responsable.username', read_only=True)
    movement_summary = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = HistorialMovimientoActivo
        fields = BaseModelSerializer.Meta.fields + [
            'activo', 'activo_codigo', 'tipo_movimiento', 'fecha_movimiento',
            'almacen_origen', 'almacen_origen_prefijo', 'almacen_destino', 'almacen_destino_prefijo',
            'estado_anterior', 'estado_nuevo', 'codigo_anterior', 'codigo_nuevo',
            'usuario_responsable', 'usuario_username', 'motivo', 'observaciones',
            'solicitud_traslado', 'metadata', 'movement_summary'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_movimiento', 'movement_summary']
    
    def get_movement_summary(self, obj):
        """Get human-readable movement summary."""
        return obj.get_movement_summary()


class AprobacionTrasladoSerializer(BaseModelSerializer):
    """Serializer for AprobacionTraslado model."""
    
    aprobador_username = serializers.CharField(source='aprobador.username', read_only=True)
    solicitud_numero = serializers.CharField(source='solicitud.numero_solicitud', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = AprobacionTraslado
        fields = BaseModelSerializer.Meta.fields + [
            'solicitud', 'solicitud_numero', 'aprobador', 'aprobador_username',
            'tipo_aprobacion', 'decision', 'fecha_decision', 'comentarios'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['fecha_decision']


class SolicitudTrasladoSerializer(BaseModelSerializer):
    """Serializer for SolicitudTraslado model."""
    
    activo_codigo = serializers.CharField(source='activo.codigo_actual', read_only=True)
    almacen_origen_nombre = serializers.CharField(source='almacen_origen.nombre', read_only=True)
    almacen_destino_nombre = serializers.CharField(source='almacen_destino.nombre', read_only=True)
    solicitante_username = serializers.CharField(source='solicitante.username', read_only=True)
    ejecutado_por_username = serializers.CharField(source='ejecutado_por.username', read_only=True)
    approval_status = serializers.SerializerMethodField()
    workflow_timeline = serializers.SerializerMethodField()
    pending_approvers = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    
    # Nested serializers for approvals
    aprobacion_origen = AprobacionTrasladoSerializer(read_only=True)
    aprobacion_destino = AprobacionTrasladoSerializer(read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = SolicitudTraslado
        fields = BaseModelSerializer.Meta.fields + [
            'numero_solicitud', 'fecha_solicitud', 'estado',
            'activo', 'activo_codigo', 'almacen_origen', 'almacen_origen_nombre',
            'almacen_destino', 'almacen_destino_nombre', 'solicitante', 'solicitante_username',
            'motivo', 'fecha_limite', 'prioridad', 'aprobacion_origen', 'aprobacion_destino',
            'fecha_ejecucion', 'ejecutado_por', 'ejecutado_por_username', 'fecha_completada',
            'observaciones', 'approval_status', 'workflow_timeline', 'pending_approvers',
            'is_overdue', 'days_until_deadline'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'numero_solicitud', 'fecha_solicitud', 'fecha_ejecucion', 'fecha_completada',
            'approval_status', 'workflow_timeline', 'pending_approvers', 'is_overdue',
            'days_until_deadline'
        ]
    
    def get_approval_status(self, obj):
        """Get detailed approval status."""
        return obj.get_approval_status()
    
    def get_workflow_timeline(self, obj):
        """Get workflow timeline."""
        return obj.get_workflow_timeline()
    
    def get_pending_approvers(self, obj):
        """Get pending approvers."""
        return obj.get_pending_approvers()
    
    def get_is_overdue(self, obj):
        """Check if request is overdue."""
        return obj.is_overdue()
    
    def get_days_until_deadline(self, obj):
        """Get days until deadline."""
        return obj.get_days_until_deadline()


class MigracionOrganizacionalSerializer(BaseModelSerializer):
    """Serializer for MigracionOrganizacional model."""
    
    migrado_por_username = serializers.CharField(source='migrado_por.username', read_only=True)
    validado_por_username = serializers.CharField(source='validado_por.username', read_only=True)
    revertido_por_username = serializers.CharField(source='revertido_por.username', read_only=True)
    old_reference_display = serializers.SerializerMethodField()
    new_reference_display = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = MigracionOrganizacional
        fields = BaseModelSerializer.Meta.fields + [
            'organizacion_central_id', 'sucursal_id', 'acueducto_id',
            'empresa', 'vicepresidencia', 'unidad_organizacional', 'acueducto_nuevo',
            'fecha_migracion', 'estado_migracion', 'validado', 'migrado_por',
            'migrado_por_username', 'validado_por', 'validado_por_username',
            'fecha_validacion', 'datos_originales', 'puede_revertir',
            'fecha_reversion', 'revertido_por', 'revertido_por_username',
            'notas', 'errores', 'warnings', 'fecha_actualizacion',
            'old_reference_display', 'new_reference_display'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'fecha_migracion', 'fecha_actualizacion', 'old_reference_display',
            'new_reference_display'
        ]
    
    def get_old_reference_display(self, obj):
        """Get display name for old structure reference."""
        return obj.get_old_reference_display()
    
    def get_new_reference_display(self, obj):
        """Get display name for new structure reference."""
        return obj.get_new_reference_display()


# ============================================================================
# BACKWARD COMPATIBILITY SERIALIZERS
# ============================================================================

class OrganizacionCentralSerializer(BaseModelSerializer):
    """Backward compatibility serializer for OrganizacionCentral."""
    
    sucursales_count = serializers.SerializerMethodField()
    parent_nombre = serializers.CharField(source='parent.nombre', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = OrganizacionCentral
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'rif', 'parent', 'parent_nombre', 'sucursales_count'
        ]
    
    def get_sucursales_count(self, obj):
        """Get count of sucursales under this organization."""
        return obj.sucursales.count()


class SucursalSerializer(BaseModelSerializer):
    """Backward compatibility serializer for Sucursal."""
    
    organizacion_nombre = serializers.CharField(source='organizacion_central.nombre', read_only=True)
    acueductos_count = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Sucursal
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'organizacion_central', 'organizacion_nombre',
            'codigo', 'direccion', 'telefono', 'acueductos_count'
        ]
    
    def get_acueductos_count(self, obj):
        """Get count of acueductos under this sucursal."""
        return obj.acueductos.count()


class AcueductoSerializer(BaseModelSerializer):
    """Backward compatibility serializer for Acueducto."""
    
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    organizacion_nombre = serializers.CharField(source='sucursal.organizacion_central.nombre', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = Acueducto
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'sucursal', 'sucursal_nombre', 'organizacion_nombre',
            'codigo', 'ubicacion'
        ]


# ============================================================================
# SPECIALIZED SERIALIZERS FOR SPECIFIC USE CASES
# ============================================================================

class AssetTrackingSerializer(BaseModelSerializer):
    """Specialized serializer for asset tracking with complete traceability."""
    
    current_location = serializers.SerializerMethodField()
    movement_history_detailed = serializers.SerializerMethodField()
    allowed_transitions = serializers.SerializerMethodField()
    can_be_transferred = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = ActivoInventario
        fields = BaseModelSerializer.Meta.fields + [
            'codigo_actual', 'codigo_original', 'tipo_activo', 'descripcion',
            'estado', 'almacen_actual', 'current_location', 'fecha_ingreso',
            'valor_unitario', 'numero_serie', 'movement_history_detailed',
            'allowed_transitions', 'can_be_transferred'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'codigo_actual', 'codigo_original', 'fecha_ingreso',
            'current_location', 'movement_history_detailed',
            'allowed_transitions', 'can_be_transferred'
        ]
    
    def get_current_location(self, obj):
        """Get human-readable current location."""
        return obj.get_current_location_display()
    
    def get_movement_history_detailed(self, obj):
        """Get detailed movement history."""
        history = obj.historial_movimientos.all()[:10]  # Last 10 movements
        return HistorialMovimientoActivoSerializer(history, many=True).data
    
    def get_allowed_transitions(self, obj):
        """Get allowed state transitions."""
        return obj.get_allowed_state_transitions()
    
    def get_can_be_transferred(self, obj):
        """Check if asset can be transferred."""
        can_transfer, message = obj.can_be_transferred()
        return {'can_transfer': can_transfer, 'message': message}


class TransferWorkflowSerializer(BaseModelSerializer):
    """Specialized serializer for transfer workflow management."""
    
    activo_details = AssetTrackingSerializer(source='activo', read_only=True)
    almacen_origen_details = AlmacenRegionalSerializer(source='almacen_origen', read_only=True)
    almacen_destino_details = AlmacenRegionalSerializer(source='almacen_destino', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = SolicitudTraslado
        fields = BaseModelSerializer.Meta.fields + [
            'numero_solicitud', 'fecha_solicitud', 'estado',
            'activo_details', 'almacen_origen_details', 'almacen_destino_details',
            'solicitante', 'motivo', 'fecha_limite', 'prioridad',
            'aprobacion_origen', 'aprobacion_destino', 'observaciones'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ['numero_solicitud', 'fecha_solicitud']


class HierarchyTreeSerializer(BaseModelSerializer):
    """Serializer for hierarchical tree representation."""
    
    children = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = Empresa  # Can be used for any MPTT model
        fields = BaseModelSerializer.Meta.fields + ['nombre', 'codigo', 'level', 'children']
    
    def get_children(self, obj):
        """Get immediate children in hierarchy."""
        if hasattr(obj, 'get_children'):
            children = obj.get_children()
            return self.__class__(children, many=True, context=self.context).data
        return []
    
    def get_level(self, obj):
        """Get hierarchy level."""
        return getattr(obj, 'level', 0)