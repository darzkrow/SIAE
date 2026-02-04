from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (
    # New hierarchical models
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    # Asset tracking models
    ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado, AprobacionTraslado,
    # Migration support models
    MigracionOrganizacional, AcueductoNuevo,
    # Legacy models
    OrganizacionCentral, Sucursal, Acueducto
)

# ============================================================================
# ADMIN PARA NUEVOS MODELOS JERÁRQUICOS
# ============================================================================

@admin.register(Empresa)
class EmpresaAdmin(MPTTModelAdmin):
    """Admin for hierarchical Empresa model"""
    list_display = ('nombre', 'codigo', 'rif', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'codigo', 'rif')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'rif', 'parent')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono', 'email')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(Vicepresidencia)
class VicepresidenciaAdmin(MPTTModelAdmin):
    """Admin for hierarchical Vicepresidencia model"""
    list_display = ('nombre', 'empresa', 'tipo', 'codigo', 'responsable', 'activo')
    list_filter = ('empresa', 'tipo', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'codigo', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ('empresa', 'responsable')
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'nombre', 'codigo', 'tipo', 'parent')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'responsable')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'empresa', 'responsable', 'parent'
        )


@admin.register(UnidadOrganizacional)
class UnidadOrganizacionalAdmin(MPTTModelAdmin):
    """Admin for hierarchical UnidadOrganizacional model"""
    list_display = ('nombre', 'vicepresidencia', 'tipo', 'codigo', 'responsable', 'activo')
    list_filter = (
        'vicepresidencia__empresa', 
        'vicepresidencia', 
        'tipo', 
        'activo', 
        'fecha_creacion'
    )
    search_fields = ('nombre', 'codigo', 'descripcion', 'ubicacion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ('vicepresidencia', 'responsable')
    fieldsets = (
        ('Información Básica', {
            'fields': ('vicepresidencia', 'nombre', 'codigo', 'tipo', 'parent')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'ubicacion', 'responsable')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'vicepresidencia__empresa', 'responsable', 'parent'
        )


@admin.register(AlmacenRegional)
class AlmacenRegionalAdmin(admin.ModelAdmin):
    """Admin for AlmacenRegional model"""
    list_display = ('prefijo', 'nombre', 'unidad_organizacional', 'manager', 'activo', 'capacidad_maxima')
    list_filter = ('activo', 'prefijo', 'unidad_organizacional__vicepresidencia')
    search_fields = ('nombre', 'prefijo', 'ubicacion', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ('unidad_organizacional', 'manager')
    fieldsets = (
        ('Información Básica', {
            'fields': ('unidad_organizacional', 'nombre', 'prefijo', 'ubicacion')
        }),
        ('Gestión', {
            'fields': ('manager', 'capacidad_maxima', 'activo')
        }),
        ('Contacto', {
            'fields': ('descripcion', 'telefono', 'email')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'unidad_organizacional__vicepresidencia__empresa', 'manager'
        )


# ============================================================================
# ADMIN PARA MODELOS DE SOPORTE DE MIGRACIÓN
# ============================================================================

@admin.register(MigracionOrganizacional)
class MigracionOrganizacionalAdmin(admin.ModelAdmin):
    """Admin for MigracionOrganizacional model"""
    list_display = (
        'id', 'get_old_reference_short', 'get_new_reference_short', 
        'estado_migracion', 'validado', 'fecha_migracion', 'migrado_por'
    )
    list_filter = (
        'estado_migracion', 'validado', 'puede_revertir', 
        'fecha_migracion', 'fecha_validacion'
    )
    search_fields = (
        'notas', 'migrado_por__username', 'validado_por__username'
    )
    readonly_fields = (
        'fecha_migracion', 'fecha_actualizacion', 'fecha_validacion', 
        'fecha_reversion', 'datos_originales', 'errores', 'warnings'
    )
    autocomplete_fields = (
        'empresa', 'vicepresidencia', 'unidad_organizacional', 
        'acueducto_nuevo', 'migrado_por', 'validado_por', 'revertido_por'
    )
    
    fieldsets = (
        ('Referencias Estructura Antigua', {
            'fields': ('organizacion_central_id', 'sucursal_id', 'acueducto_id'),
            'description': 'IDs de los registros en la estructura organizacional antigua'
        }),
        ('Referencias Estructura Nueva', {
            'fields': ('empresa', 'vicepresidencia', 'unidad_organizacional', 'acueducto_nuevo'),
            'description': 'Referencias a los nuevos modelos jerárquicos'
        }),
        ('Estado de Migración', {
            'fields': ('estado_migracion', 'validado', 'puede_revertir'),
        }),
        ('Responsables', {
            'fields': ('migrado_por', 'validado_por', 'revertido_por'),
        }),
        ('Fechas', {
            'fields': ('fecha_migracion', 'fecha_validacion', 'fecha_reversion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
        ('Notas y Observaciones', {
            'fields': ('notas',),
        }),
        ('Datos Técnicos', {
            'fields': ('datos_originales', 'errores', 'warnings'),
            'classes': ('collapse',),
            'description': 'Información técnica de la migración (solo lectura)'
        }),
    )
    
    actions = ['marcar_como_completada', 'validar_migraciones', 'revertir_migraciones']
    
    def get_old_reference_short(self, obj):
        """Short display for old reference"""
        display = obj.get_old_reference_display()
        return display[:50] + '...' if len(display) > 50 else display
    get_old_reference_short.short_description = 'Referencia Antigua'
    
    def get_new_reference_short(self, obj):
        """Short display for new reference"""
        display = obj.get_new_reference_display()
        return display[:50] + '...' if len(display) > 50 else display
    get_new_reference_short.short_description = 'Referencia Nueva'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'empresa', 'vicepresidencia', 'unidad_organizacional', 
            'acueducto_nuevo', 'migrado_por', 'validado_por', 'revertido_por'
        )
    
    def marcar_como_completada(self, request, queryset):
        """Admin action to mark migrations as completed"""
        updated = 0
        for migracion in queryset.filter(estado_migracion='PENDIENTE'):
            try:
                migracion.marcar_como_completada(request.user)
                updated += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error al completar migración {migracion.id}: {str(e)}',
                    level='ERROR'
                )
        
        if updated:
            self.message_user(
                request, 
                f'{updated} migración(es) marcada(s) como completada(s).'
            )
    marcar_como_completada.short_description = 'Marcar como completada'
    
    def validar_migraciones(self, request, queryset):
        """Admin action to validate migrations"""
        updated = 0
        for migracion in queryset.filter(estado_migracion='COMPLETADA', validado=False):
            try:
                migracion.validar_migracion(request.user)
                updated += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error al validar migración {migracion.id}: {str(e)}',
                    level='ERROR'
                )
        
        if updated:
            self.message_user(
                request, 
                f'{updated} migración(es) validada(s).'
            )
    validar_migraciones.short_description = 'Validar migraciones'
    
    def revertir_migraciones(self, request, queryset):
        """Admin action to revert migrations"""
        updated = 0
        for migracion in queryset.filter(puede_revertir=True).exclude(estado_migracion='REVERTIDA'):
            try:
                migracion.revertir_migracion(request.user, 'Revertida desde admin')
                updated += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error al revertir migración {migracion.id}: {str(e)}',
                    level='ERROR'
                )
        
        if updated:
            self.message_user(
                request, 
                f'{updated} migración(es) revertida(s).'
            )
    revertir_migraciones.short_description = 'Revertir migraciones'


@admin.register(AcueductoNuevo)
class AcueductoNuevoAdmin(admin.ModelAdmin):
    """Admin for AcueductoNuevo model"""
    list_display = (
        'nombre', 'codigo', 'tipo_sistema', 'unidad_organizacional', 
        'responsable_operativo', 'activo', 'fecha_creacion'
    )
    list_filter = (
        'tipo_sistema', 'activo', 'fecha_creacion',
        'unidad_organizacional__vicepresidencia__empresa',
        'unidad_organizacional__vicepresidencia',
        'unidad_organizacional'
    )
    search_fields = (
        'nombre', 'codigo', 'ubicacion', 
        'unidad_organizacional__nombre', 'unidad_organizacional__codigo'
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ('unidad_organizacional', 'responsable_operativo', 'creado_por')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('unidad_organizacional', 'tipo_sistema', 'nombre', 'codigo')
        }),
        ('Responsabilidad', {
            'fields': ('responsable_operativo',)
        }),
        ('Ubicación y Capacidad', {
            'fields': ('ubicacion', 'capacidad_produccion', 'poblacion_servida')
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_inauguracion',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'creado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'unidad_organizacional__vicepresidencia__empresa',
            'responsable_operativo', 'creado_por'
        )


# ============================================================================
# ADMIN PARA ASSET TRACKING MODELS
# ============================================================================

@admin.register(ActivoInventario)
class ActivoInventarioAdmin(admin.ModelAdmin):
    """Admin for ActivoInventario model"""
    list_display = [
        'codigo_actual', 'tipo_activo', 'descripcion', 
        'almacen_actual', 'estado', 'valor_unitario', 'fecha_ingreso'
    ]
    list_filter = [
        'tipo_activo', 'estado', 'almacen_actual', 
        'almacen_actual__unidad_organizacional__vicepresidencia',
        'fecha_ingreso'
    ]
    search_fields = ['codigo_actual', 'codigo_original', 'descripcion', 'numero_serie']
    readonly_fields = [
        'codigo_actual', 'codigo_original', 'fecha_ingreso', 
        'fecha_actualizacion', 'creado_por', 'actualizado_por'
    ]
    autocomplete_fields = ['almacen_actual', 'creado_por', 'actualizado_por']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_actual', 'codigo_original', 'tipo_activo', 'descripcion')
        }),
        ('Ubicación y Estado', {
            'fields': ('almacen_actual', 'estado')
        }),
        ('Detalles del Activo', {
            'fields': ('valor_unitario', 'numero_serie')
        }),
        ('Relación con Inventario', {
            'fields': ('producto_inventario_type', 'producto_inventario_id'),
            'description': 'Relación genérica con productos del inventario'
        }),
        ('Auditoría', {
            'fields': ('fecha_ingreso', 'fecha_actualizacion', 'creado_por', 'actualizado_por'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'almacen_actual__unidad_organizacional__vicepresidencia',
            'producto_inventario_type', 'creado_por', 'actualizado_por'
        )
    
    def save_model(self, request, obj, form, change):
        """Set user fields when saving"""
        if not change:  # Creating new asset
            obj.creado_por = request.user
        else:  # Updating existing asset
            obj.actualizado_por = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['export_asset_codes', 'validate_asset_codes']
    
    def export_asset_codes(self, request, queryset):
        """Export asset codes for selected assets"""
        codes = [asset.codigo_actual for asset in queryset]
        self.message_user(
            request,
            f'Códigos de activos: {", ".join(codes)}'
        )
    export_asset_codes.short_description = 'Exportar códigos de activos'
    
    def validate_asset_codes(self, request, queryset):
        """Validate asset codes format"""
        invalid_count = 0
        for asset in queryset:
            if not ActivoInventario.validate_asset_code_format(asset.codigo_actual):
                invalid_count += 1
        
        if invalid_count == 0:
            self.message_user(request, 'Todos los códigos de activos son válidos.')
        else:
            self.message_user(
                request,
                f'{invalid_count} activo(s) tienen códigos inválidos.',
                level='WARNING'
            )
    validate_asset_codes.short_description = 'Validar códigos de activos'


@admin.register(HistorialMovimientoActivo)
class HistorialMovimientoActivoAdmin(admin.ModelAdmin):
    """Admin for HistorialMovimientoActivo model (read-only audit trail)"""
    list_display = [
        'activo', 'tipo_movimiento', 'fecha_movimiento',
        'almacen_origen', 'almacen_destino', 'estado_anterior', 'estado_nuevo',
        'usuario_responsable'
    ]
    list_filter = [
        'tipo_movimiento', 'fecha_movimiento', 'almacen_origen', 'almacen_destino',
        'estado_anterior', 'estado_nuevo'
    ]
    search_fields = ['activo__codigo_actual', 'motivo', 'observaciones']
    readonly_fields = [
        'activo', 'tipo_movimiento', 'fecha_movimiento', 'almacen_origen', 'almacen_destino',
        'estado_anterior', 'estado_nuevo', 'codigo_anterior', 'codigo_nuevo',
        'usuario_responsable', 'motivo', 'observaciones', 'solicitud_traslado'
    ]
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('activo', 'tipo_movimiento', 'fecha_movimiento')
        }),
        ('Ubicaciones', {
            'fields': ('almacen_origen', 'almacen_destino')
        }),
        ('Cambios de Estado', {
            'fields': ('estado_anterior', 'estado_nuevo')
        }),
        ('Evolución de Códigos', {
            'fields': ('codigo_anterior', 'codigo_nuevo')
        }),
        ('Responsables', {
            'fields': ('usuario_responsable',)
        }),
        ('Detalles', {
            'fields': ('motivo', 'observaciones', 'solicitud_traslado')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'activo', 'almacen_origen', 'almacen_destino', 'usuario_responsable', 'solicitud_traslado'
        )
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit records"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent modification of audit records"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit records"""
        return False


@admin.register(SolicitudTraslado)
class SolicitudTrasladoAdmin(admin.ModelAdmin):
    """Admin for SolicitudTraslado model"""
    list_display = [
        'numero_solicitud', 'activo', 'almacen_origen', 'almacen_destino',
        'estado', 'prioridad', 'fecha_solicitud', 'solicitante'
    ]
    list_filter = [
        'estado', 'prioridad', 'fecha_solicitud', 'almacen_origen', 'almacen_destino'
    ]
    search_fields = ['numero_solicitud', 'activo__codigo_actual', 'motivo']
    readonly_fields = [
        'numero_solicitud', 'fecha_solicitud', 'fecha_ejecucion', 'fecha_completada'
    ]
    autocomplete_fields = [
        'activo', 'almacen_origen', 'almacen_destino', 'solicitante', 'ejecutado_por'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_solicitud', 'fecha_solicitud', 'estado', 'prioridad')
        }),
        ('Activo y Ubicaciones', {
            'fields': ('activo', 'almacen_origen', 'almacen_destino')
        }),
        ('Solicitud', {
            'fields': ('solicitante', 'motivo', 'fecha_limite')
        }),
        ('Aprobaciones', {
            'fields': ('aprobacion_origen', 'aprobacion_destino'),
            'classes': ('collapse',)
        }),
        ('Ejecución', {
            'fields': ('fecha_ejecucion', 'ejecutado_por', 'fecha_completada'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'activo', 'almacen_origen', 'almacen_destino', 'solicitante', 'ejecutado_por'
        )
    
    actions = ['approve_origin', 'approve_destination', 'execute_transfers']
    
    def approve_origin(self, request, queryset):
        """Approve transfers from origin warehouse"""
        approved = 0
        for solicitud in queryset.filter(estado='PENDIENTE'):
            if solicitud.can_approve_origin(request.user):
                try:
                    solicitud.approve_origin(request.user, 'Aprobado desde admin')
                    approved += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error al aprobar {solicitud.numero_solicitud}: {str(e)}',
                        level='ERROR'
                    )
        
        if approved:
            self.message_user(request, f'{approved} solicitud(es) aprobada(s) desde origen.')
    approve_origin.short_description = 'Aprobar desde origen'
    
    def approve_destination(self, request, queryset):
        """Approve transfers from destination warehouse"""
        approved = 0
        for solicitud in queryset.filter(estado__in=['PENDIENTE', 'APROBADA_ORIGEN']):
            if solicitud.can_approve_destination(request.user):
                try:
                    solicitud.approve_destination(request.user, 'Aprobado desde admin')
                    approved += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error al aprobar {solicitud.numero_solicitud}: {str(e)}',
                        level='ERROR'
                    )
        
        if approved:
            self.message_user(request, f'{approved} solicitud(es) aprobada(s) desde destino.')
    approve_destination.short_description = 'Aprobar desde destino'
    
    def execute_transfers(self, request, queryset):
        """Execute approved transfers"""
        executed = 0
        for solicitud in queryset.filter(estado='APROBADA_COMPLETA'):
            try:
                solicitud.execute_transfer(request.user)
                executed += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error al ejecutar {solicitud.numero_solicitud}: {str(e)}',
                    level='ERROR'
                )
        
        if executed:
            self.message_user(request, f'{executed} traslado(s) ejecutado(s).')
    execute_transfers.short_description = 'Ejecutar traslados'


@admin.register(AprobacionTraslado)
class AprobacionTrasladoAdmin(admin.ModelAdmin):
    """Admin for AprobacionTraslado model"""
    list_display = [
        'solicitud', 'tipo_aprobacion', 'aprobador', 'decision', 'fecha_decision'
    ]
    list_filter = ['tipo_aprobacion', 'decision', 'fecha_decision']
    search_fields = ['solicitud__numero_solicitud', 'comentarios']
    readonly_fields = ['fecha_decision']
    autocomplete_fields = ['solicitud', 'aprobador']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('solicitud', 'tipo_aprobacion', 'aprobador')
        }),
        ('Decisión', {
            'fields': ('decision', 'fecha_decision', 'comentarios')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'solicitud', 'aprobador'
        )
    
    def save_model(self, request, obj, form, change):
        """Set created_by field when creating new acueducto"""
        if not change:  # Only when creating
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# ADMIN PARA MODELOS LEGACY (Mantener compatibilidad)
# ============================================================================

@admin.register(OrganizacionCentral)
class OrganizacionCentralAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rif')
    search_fields = ('nombre', 'rif')

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'organizacion_central', 'codigo')
    search_fields = ('nombre', 'codigo')
    list_filter = ('organizacion_central',)

@admin.register(Acueducto)
class AcueductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sucursal', 'codigo')
    search_fields = ('nombre', 'codigo')
    list_filter = ('sucursal__organizacion_central', 'sucursal')
