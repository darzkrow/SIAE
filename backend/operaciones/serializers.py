"""
Serializers for Operaciones App.
Handles asset tracking, transfer workflows, and audit trails.
"""
from rest_framework import serializers
from core.serializers import BaseModelSerializer
from django.contrib.auth import get_user_model
from .models import (
    ActivoInventario, HistorialMovimientoActivo,
    SolicitudTraslado, AprobacionTraslado,
    AuditoriaEstadoActivo, AuditoriaAprobacion,
    AuditoriaOperacionSistema, AuditoriaAccesoSistema
)

User = get_user_model()


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
        # Note: If get_movement_summary is not yet in the model, this might fail.
        # But it was in the institucion/models.py version.
        if hasattr(obj, 'get_movement_summary'):
            return obj.get_movement_summary()
        return f"{obj.get_tipo_movimiento_display()} para {obj.activo.codigo_actual}"


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
    ejecutor_username = serializers.CharField(source='ejecutor.username', read_only=True)
    approval_status = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    
    # Nested serializers for approvals
    aprobacion_origen_details = AprobacionTrasladoSerializer(source='aprobacion_origen', read_only=True)
    aprobacion_destino_details = AprobacionTrasladoSerializer(source='aprobacion_destino', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = SolicitudTraslado
        fields = BaseModelSerializer.Meta.fields + [
            'numero_solicitud', 'fecha_solicitud', 'estado',
            'activo', 'activo_codigo', 'almacen_origen', 'almacen_origen_nombre',
            'almacen_destino', 'almacen_destino_nombre', 'solicitante', 'solicitante_username',
            'motivo', 'fecha_limite', 'prioridad', 'aprobacion_origen', 'aprobacion_destino',
            'aprobacion_origen_details', 'aprobacion_destino_details',
            'fecha_ejecucion', 'ejecutor', 'ejecutor_username', 'fecha_completado',
            'observaciones', 'approval_status', 'is_overdue', 'days_until_deadline',
            'qr_code'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'numero_solicitud', 'fecha_solicitud', 'fecha_ejecucion', 'fecha_completado',
            'approval_status', 'is_overdue', 'days_until_deadline', 'qr_code'
        ]
    
    def get_approval_status(self, obj):
        """Get detailed approval status."""
        return obj.get_approval_status()
    
    def get_is_overdue(self, obj):
        """Check if request is overdue."""
        return obj.is_overdue()
    
    def get_days_until_deadline(self, obj):
        """Get days until deadline."""
        return obj.get_days_until_deadline()


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


class AuditoriaEstadoActivoSerializer(BaseModelSerializer):
    """Serializer for AuditoriaEstadoActivo model."""
    usuario_username = serializers.CharField(source='usuario_responsable.username', read_only=True)
    activo_codigo = serializers.CharField(source='activo.codigo_actual', read_only=True)
    
    class Meta:
        model = AuditoriaEstadoActivo
        fields = '__all__'


class AuditoriaAprobacionSerializer(BaseModelSerializer):
    """Serializer for AuditoriaAprobacion model."""
    usuario_username = serializers.CharField(source='usuario_responsable.username', read_only=True)
    solicitud_numero = serializers.CharField(source='solicitud_traslado.numero_solicitud', read_only=True)
    
    class Meta:
        model = AuditoriaAprobacion
        fields = '__all__'


class AuditoriaOperacionSistemaSerializer(BaseModelSerializer):
    """Serializer for AuditoriaOperacionSistema model."""
    usuario_username = serializers.CharField(source='usuario_responsable.username', read_only=True)
    
    class Meta:
        model = AuditoriaOperacionSistema
        fields = '__all__'


class AuditoriaAccesoSistemaSerializer(BaseModelSerializer):
    """Serializer for AuditoriaAccesoSistema model."""
    usuario_username = serializers.CharField(source='usuario_responsable.username', read_only=True)
    usuario_objetivo_username = serializers.CharField(source='usuario_objetivo.username', read_only=True)
    
    class Meta:
        model = AuditoriaAccesoSistema
        fields = '__all__'
