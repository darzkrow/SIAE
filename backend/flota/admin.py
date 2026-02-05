"""
Flota Admin - Fleet Management Admin Configuration
"""
from django.contrib import admin
from .models import (
    TipoVehiculo,
    Vehiculo,
    DocumentoVehiculo,
    MantenimientoVehiculo,
    AsignacionVehiculo,
    RegistroCombustible,
)


@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    """Admin para tipos de vehículos"""
    list_display = ['codigo', 'nombre', 'categoria', 'requiere_licencia_especial', 'activo']
    list_filter = ['categoria', 'activo', 'requiere_licencia_especial']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering = ['categoria', 'nombre']


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    """Admin para vehículos"""
    list_display = [
        'codigo', 'placa', 'marca', 'modelo', 'año',
        'tipo_vehiculo', 'estado', 'kilometraje_actual',
        'responsable_actual', 'activo'
    ]
    list_filter = ['estado', 'tipo_vehiculo', 'activo', 'tipo_combustible']
    search_fields = ['codigo', 'placa', 'serial_motor', 'serial_carroceria', 'marca', 'modelo']
    ordering = ['-created_at']
    readonly_fields = ['codigo', 'qr_code', 'created_at', 'updated_at']


@admin.register(DocumentoVehiculo)
class DocumentoVehiculoAdmin(admin.ModelAdmin):
    """Admin para documentos de vehículos"""
    list_display = [
        'vehiculo', 'tipo_documento', 'nombre',
        'fecha_emision', 'fecha_vencimiento', 'esta_vencido'
    ]
    list_filter = ['tipo_documento', 'alertar_vencimiento', 'alerta_enviada']
    search_fields = ['vehiculo__codigo', 'vehiculo__placa', 'nombre', 'numero_documento']
    ordering = ['fecha_vencimiento']
    readonly_fields = ['created_at', 'updated_at', 'alerta_enviada']
    
    def esta_vencido(self, obj):
        return obj.esta_vencido
    esta_vencido.boolean = True
    esta_vencido.short_description = 'Vencido'


@admin.register(MantenimientoVehiculo)
class MantenimientoVehiculoAdmin(admin.ModelAdmin):
    """Admin para mantenimientos"""
    list_display = [
        'vehiculo', 'tipo_mantenimiento', 'estado',
        'fecha_programada', 'costo_total', 'solicitado_por'
    ]
    list_filter = ['tipo_mantenimiento', 'estado']
    search_fields = ['vehiculo__codigo', 'vehiculo__placa', 'descripcion']
    ordering = ['-fecha_programada']
    readonly_fields = ['costo_total', 'created_at', 'updated_at']


@admin.register(AsignacionVehiculo)
class AsignacionVehiculoAdmin(admin.ModelAdmin):
    """Admin para asignaciones"""
    list_display = [
        'vehiculo', 'usuario_asignado', 'tipo_asignacion',
        'fecha_inicio', 'fecha_fin', 'activa'
    ]
    list_filter = ['tipo_asignacion', 'activa']
    search_fields = ['vehiculo__codigo', 'vehiculo__placa']
    ordering = ['-fecha_inicio']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RegistroCombustible)
class RegistroCombustibleAdmin(admin.ModelAdmin):
    """Admin para registros de combustible"""
    list_display = [
        'vehiculo', 'fecha', 'tipo_combustible',
        'litros', 'costo', 'kilometraje', 'registrado_por'
    ]
    list_filter = ['tipo_combustible', 'tanque_lleno']
    search_fields = ['vehiculo__codigo', 'vehiculo__placa', 'estacion_servicio']
    ordering = ['-fecha']
    readonly_fields = ['precio_por_litro', 'created_at', 'updated_at']
