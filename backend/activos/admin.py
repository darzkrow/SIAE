from django.contrib import admin
from activos.models import (
    MaterialEstrategico, ActivoFijo, 
    FichaTecnicaMotor, RegistroMantenimiento
)

class RegistroMantenimientoInline(admin.TabularInline):
    model = RegistroMantenimiento
    extra = 1
    fields = ['tipo_mantenimiento', 'fecha_vencimiento', 'prioridad', 'realizado']

@admin.register(MaterialEstrategico)
class MaterialEstrategicoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'nivel_criticidad', 'stock_seguridad_dias', 'responsable']
    list_filter = ['nivel_criticidad', 'prioridad_reposicion']
    search_fields = ['plan_contingencia']
    autocomplete_fields = ['proveedor_alternativo', 'responsable']

@admin.register(ActivoFijo)
class ActivoFijoAdmin(admin.ModelAdmin):
    list_display = ['codigo_activo', 'producto', 'valor_adquisicion', 'estado_fisico', 'fecha_adquisicion']
    list_filter = ['estado_fisico', 'estado_depreciacion', 'ubicacion']
    search_fields = ['codigo_activo']
    autocomplete_fields = ['ubicacion', 'responsable']

@admin.register(FichaTecnicaMotor)
class FichaTecnicaMotorAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'estado_actual', 'potencia_nominal_kw', 'tension_v']
    list_filter = ['estado_actual', 'clase_aislamiento']
    search_fields = ['numero_fases']
    inlines = [RegistroMantenimientoInline]

@admin.register(RegistroMantenimiento)
class RegistroMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['ficha_tecnica', 'tipo_mantenimiento', 'prioridad', 'realizado', 'fecha_registro']
    list_filter = ['tipo_mantenimiento', 'prioridad', 'realizado']
    search_fields = ['descripcion_cambios']
