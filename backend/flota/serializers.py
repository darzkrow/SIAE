"""
Flota Serializers - Fleet Management API
"""
from rest_framework import serializers
from .models import (
    TipoVehiculo,
    Vehiculo,
    DocumentoVehiculo,
    MantenimientoVehiculo,
    AsignacionVehiculo,
    RegistroCombustible,
)


class TipoVehiculoSerializer(serializers.ModelSerializer):
    """Serializer para catálogo de tipos de vehículos"""
    categoria_display = serializers.CharField(
        source='get_categoria_display',
        read_only=True
    )
    
    class Meta:
        model = TipoVehiculo
        fields = [
            'id', 'nombre', 'categoria', 'categoria_display', 'codigo',
            'descripcion', 'requiere_licencia_especial', 'tipo_licencia_requerida',
            'usa_kilometraje', 'usa_horas_motor',
            'km_mantenimiento_preventivo', 'horas_mantenimiento_preventivo',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VehiculoListSerializer(serializers.ModelSerializer):
    """Serializer para listado de vehículos (resumen)"""
    tipo_vehiculo_nombre = serializers.CharField(
        source='tipo_vehiculo.nombre',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    responsable_nombre = serializers.SerializerMethodField()
    necesita_mantenimiento = serializers.BooleanField(read_only=True)
    km_para_mantenimiento = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = [
            'id', 'codigo', 'placa', 'marca', 'modelo', 'año', 'color',
            'tipo_vehiculo', 'tipo_vehiculo_nombre',
            'estado', 'estado_display',
            'kilometraje_actual', 'horas_motor_actual',
            'responsable_actual', 'responsable_nombre',
            'necesita_mantenimiento', 'km_para_mantenimiento',
            'activo'
        ]
    
    def get_responsable_nombre(self, obj):
        if obj.responsable_actual:
            return obj.responsable_actual.get_full_name()
        return None


class VehiculoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para vehículo individual"""
    tipo_vehiculo_detail = TipoVehiculoSerializer(
        source='tipo_vehiculo',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    tipo_combustible_display = serializers.CharField(
        source='get_tipo_combustible_display',
        read_only=True
    )
    transmision_display = serializers.CharField(
        source='get_transmision_display',
        read_only=True
    )
    responsable_nombre = serializers.SerializerMethodField()
    unidad_nombre = serializers.CharField(
        source='unidad_organizacional.nombre',
        read_only=True
    )
    almacen_nombre = serializers.SerializerMethodField()
    proveedor_nombre = serializers.SerializerMethodField()
    
    # Campos calculados
    necesita_mantenimiento = serializers.BooleanField(read_only=True)
    km_para_mantenimiento = serializers.IntegerField(read_only=True)
    horas_para_mantenimiento = serializers.IntegerField(read_only=True)
    
    # Contadores
    total_documentos = serializers.SerializerMethodField()
    documentos_vencidos = serializers.SerializerMethodField()
    total_mantenimientos = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehiculo
        fields = '__all__'
        read_only_fields = [
            'codigo', 'created_at', 'updated_at', 'qr_code',
            'ultimo_mantenimiento_fecha', 'ultimo_mantenimiento_km',
            'ultimo_mantenimiento_horas'
        ]
    
    def get_responsable_nombre(self, obj):
        if obj.responsable_actual:
            return obj.responsable_actual.get_full_name()
        return None
    
    def get_almacen_nombre(self, obj):
        if obj.almacen_actual:
            return obj.almacen_actual.nombre
        return None
    
    def get_proveedor_nombre(self, obj):
        if obj.proveedor:
            return obj.proveedor.nombre
        return None
    
    def get_total_documentos(self, obj):
        return obj.documentos.count()
    
    def get_documentos_vencidos(self, obj):
        from django.utils import timezone
        return obj.documentos.filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).count()
    
    def get_total_mantenimientos(self, obj):
        return obj.mantenimientos.filter(estado='COMPLETADO').count()


class VehiculoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear vehículos"""
    
    class Meta:
        model = Vehiculo
        fields = [
            'tipo_vehiculo', 'placa', 'serial_motor', 'serial_carroceria',
            'numero_matricula', 'marca', 'modelo', 'año', 'color',
            'tipo_combustible', 'transmision', 'capacidad_pasajeros',
            'capacidad_carga_kg', 'capacidad_tanque',
            'unidad_organizacional', 'almacen_actual',
            'valor_adquisicion', 'fecha_adquisicion', 'proveedor',
            'numero_factura', 'observaciones'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creado_por'] = request.user
        return super().create(validated_data)


class DocumentoVehiculoSerializer(serializers.ModelSerializer):
    """Serializer para documentos de vehículos"""
    tipo_documento_display = serializers.CharField(
        source='get_tipo_documento_display',
        read_only=True
    )
    vehiculo_codigo = serializers.CharField(
        source='vehiculo.codigo',
        read_only=True
    )
    esta_vencido = serializers.BooleanField(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    requiere_alerta = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DocumentoVehiculo
        fields = [
            'id', 'vehiculo', 'vehiculo_codigo',
            'tipo_documento', 'tipo_documento_display',
            'nombre', 'numero_documento',
            'fecha_emision', 'fecha_vencimiento',
            'archivo', 'alertar_vencimiento', 'dias_alerta',
            'esta_vencido', 'dias_para_vencer', 'requiere_alerta',
            'subido_por', 'observaciones',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'alerta_enviada']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['subido_por'] = request.user
        return super().create(validated_data)


class MantenimientoVehiculoSerializer(serializers.ModelSerializer):
    """Serializer para mantenimientos"""
    tipo_mantenimiento_display = serializers.CharField(
        source='get_tipo_mantenimiento_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    vehiculo_codigo = serializers.CharField(
        source='vehiculo.codigo',
        read_only=True
    )
    vehiculo_placa = serializers.CharField(
        source='vehiculo.placa',
        read_only=True
    )
    proveedor_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = MantenimientoVehiculo
        fields = [
            'id', 'vehiculo', 'vehiculo_codigo', 'vehiculo_placa',
            'tipo_mantenimiento', 'tipo_mantenimiento_display',
            'estado', 'estado_display',
            'fecha_programada', 'fecha_inicio', 'fecha_fin',
            'kilometraje_servicio', 'horas_motor_servicio',
            'descripcion', 'trabajos_realizados', 'repuestos_utilizados',
            'costo_mano_obra', 'costo_repuestos', 'costo_total',
            'proveedor_servicio', 'proveedor_nombre', 'numero_factura',
            'solicitado_por', 'realizado_por', 'observaciones',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'costo_total']
    
    def get_proveedor_nombre(self, obj):
        if obj.proveedor_servicio:
            return obj.proveedor_servicio.nombre
        return None
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['solicitado_por'] = request.user
        return super().create(validated_data)


class AsignacionVehiculoSerializer(serializers.ModelSerializer):
    """Serializer para asignaciones de vehículos"""
    tipo_asignacion_display = serializers.CharField(
        source='get_tipo_asignacion_display',
        read_only=True
    )
    vehiculo_codigo = serializers.CharField(
        source='vehiculo.codigo',
        read_only=True
    )
    usuario_nombre = serializers.SerializerMethodField()
    unidad_nombre = serializers.CharField(
        source='unidad_destino.nombre',
        read_only=True
    )
    kilometros_recorridos = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = AsignacionVehiculo
        fields = [
            'id', 'vehiculo', 'vehiculo_codigo',
            'usuario_asignado', 'usuario_nombre',
            'tipo_asignacion', 'tipo_asignacion_display',
            'unidad_destino', 'unidad_nombre',
            'fecha_inicio', 'fecha_fin', 'activa',
            'kilometraje_inicial', 'kilometraje_final',
            'horas_motor_inicial', 'horas_motor_final',
            'kilometros_recorridos',
            'motivo', 'observaciones',
            'asignado_por',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'activa',
            'fecha_fin', 'kilometraje_final', 'horas_motor_final'
        ]
    
    def get_usuario_nombre(self, obj):
        return obj.usuario_asignado.get_full_name()
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['asignado_por'] = request.user
        return super().create(validated_data)


class RegistroCombustibleSerializer(serializers.ModelSerializer):
    """Serializer para registros de combustible"""
    tipo_combustible_display = serializers.CharField(
        source='get_tipo_combustible_display',
        read_only=True
    )
    vehiculo_codigo = serializers.CharField(
        source='vehiculo.codigo',
        read_only=True
    )
    vehiculo_placa = serializers.CharField(
        source='vehiculo.placa',
        read_only=True
    )
    rendimiento_km_por_litro = serializers.FloatField(read_only=True)
    conductor_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroCombustible
        fields = [
            'id', 'vehiculo', 'vehiculo_codigo', 'vehiculo_placa',
            'fecha', 'tipo_combustible', 'tipo_combustible_display',
            'litros', 'costo', 'precio_por_litro',
            'kilometraje', 'horas_motor', 'tanque_lleno',
            'estacion_servicio',
            'registrado_por', 'conductor', 'conductor_nombre',
            'rendimiento_km_por_litro',
            'observaciones',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'precio_por_litro']
    
    def get_conductor_nombre(self, obj):
        if obj.conductor:
            return obj.conductor.get_full_name()
        return None
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['registrado_por'] = request.user
        return super().create(validated_data)


# =============================================================================
# SERIALIZERS PARA ACCIONES ESPECIALES
# =============================================================================

class FinalizarAsignacionSerializer(serializers.Serializer):
    """Serializer para finalizar una asignación"""
    kilometraje_final = serializers.IntegerField(required=False)
    horas_motor_final = serializers.IntegerField(required=False)
    observaciones = serializers.CharField(required=False, allow_blank=True)


class ActualizarKilometrajeSerializer(serializers.Serializer):
    """Serializer para actualizar kilometraje"""
    kilometraje = serializers.IntegerField(min_value=0)


class ActualizarHorasMotorSerializer(serializers.Serializer):
    """Serializer para actualizar horas de motor"""
    horas_motor = serializers.IntegerField(min_value=0)


class CompletarMantenimientoSerializer(serializers.Serializer):
    """Serializer para completar un mantenimiento"""
    trabajos_realizados = serializers.CharField()
    repuestos_utilizados = serializers.CharField(required=False, allow_blank=True)
    costo_mano_obra = serializers.DecimalField(max_digits=12, decimal_places=2)
    costo_repuestos = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = serializers.CharField(required=False, allow_blank=True)
