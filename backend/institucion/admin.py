"""
Admin configuration for institucion app
"""
from django.contrib import admin
from .models import (
    Subalmacen,
    Empresa,
    Vicepresidencia,
    UnidadOrganizacional,
    AlmacenRegional,
    ActivoInventario,
    SolicitudTraslado,
    AprobacionTraslado,
    OrganizacionCentral,
    Sucursal,
    Acueducto,
)


@admin.register(Subalmacen)
class SubalmacenAdmin(admin.ModelAdmin):
    """Admin para Subalmacén"""
    list_display = ['codigo', 'nombre', 'sucursal', 'estado', 'municipio', 'responsable', 'activo']
    list_filter = ['activo', 'estado', 'municipio', 'sucursal']
    search_fields = ['nombre', 'codigo', 'direccion']
    ordering = ['estado__name', 'sucursal__nombre', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'sucursal', 'activo')
        }),
        ('Ubicación Geográfica', {
            'fields': ('estado', 'municipio', 'parroquia', 'direccion', 'coordenadas_gps')
        }),
        ('Gestión', {
            'fields': ('responsable', 'capacidad', 'descripcion')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'sucursal', 'estado', 'municipio', 'parroquia', 'responsable'
        )


# Register other models with basic admin
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo']
    search_fields = ['nombre', 'codigo']


@admin.register(Vicepresidencia)
class VicepresidenciaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'empresa', 'activo']
    list_filter = ['empresa', 'activo']
    search_fields = ['nombre', 'codigo']


@admin.register(UnidadOrganizacional)
class UnidadOrganizacionalAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'vicepresidencia', 'activo']
    list_filter = ['vicepresidencia', 'activo']
    search_fields = ['nombre', 'codigo']


@admin.register(AlmacenRegional)
class AlmacenRegionalAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'unidad_organizacional', 'activo']
    list_filter = ['unidad_organizacional', 'activo']
    search_fields = ['nombre', 'codigo']


@admin.register(ActivoInventario)
class ActivoInventarioAdmin(admin.ModelAdmin):
    list_display = ['codigo_actual', 'tipo_activo', 'almacen_actual', 'estado']
    list_filter = ['tipo_activo', 'estado', 'almacen_actual']
    search_fields = ['codigo_actual', 'codigo_anterior']


@admin.register(SolicitudTraslado)
class SolicitudTrasladoAdmin(admin.ModelAdmin):
    list_display = ['numero_solicitud', 'estado', 'activo', 'almacen_origen', 'almacen_destino', 'fecha_solicitud']
    list_filter = ['estado', 'prioridad', 'fecha_solicitud']
    search_fields = ['numero_solicitud']
    readonly_fields = ['qr_code', 'qr_url', 'qr_generado_en']


@admin.register(AprobacionTraslado)
class AprobacionTrasladoAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'tipo_aprobacion', 'aprobador', 'decision', 'fecha_aprobacion']
    list_filter = ['tipo_aprobacion', 'decision']


@admin.register(OrganizacionCentral)
class OrganizacionCentralAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre']
    search_fields = ['nombre', 'codigo']


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'organizacion_central']
    list_filter = ['organizacion_central']
    search_fields = ['nombre', 'codigo']


@admin.register(Acueducto)
class AcueductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'sucursal']
    list_filter = ['sucursal']
    search_fields = ['nombre', 'codigo']
