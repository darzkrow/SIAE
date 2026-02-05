"""
Tareas Admin - Task Scheduling Admin Configuration
"""
from django.contrib import admin
from .models import (
    CategoriaTarea,
    ColumnaKanban,
    Tarea,
    AsignacionTarea,
    ComentarioTarea,
    ArchivoAdjunto,
    RecordatorioTarea,
    HistorialTarea,
)


@admin.register(CategoriaTarea)
class CategoriaTareaAdmin(admin.ModelAdmin):
    """Admin para categorías de tareas"""
    list_display = ['codigo', 'nombre', 'color', 'orden', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'codigo']
    ordering = ['orden', 'nombre']
    list_editable = ['orden', 'activo']


@admin.register(ColumnaKanban)
class ColumnaKanbanAdmin(admin.ModelAdmin):
    """Admin para columnas Kanban"""
    list_display = ['nombre', 'tipo', 'orden', 'limite_tareas', 'activo']
    list_filter = ['tipo', 'activo']
    ordering = ['orden']
    list_editable = ['orden', 'activo']


class AsignacionInline(admin.TabularInline):
    """Inline para asignaciones"""
    model = AsignacionTarea
    extra = 0
    fields = ['usuario', 'rol', 'asignado_por', 'notificado']
    readonly_fields = ['asignado_por', 'notificado']


class ComentarioInline(admin.TabularInline):
    """Inline para comentarios"""
    model = ComentarioTarea
    extra = 0
    fields = ['autor', 'contenido', 'created_at']
    readonly_fields = ['autor', 'created_at']


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    """Admin para tareas"""
    list_display = [
        'titulo', 'categoria', 'prioridad', 'estado',
        'fecha_vencimiento', 'creador', 'porcentaje_completado'
    ]
    list_filter = ['estado', 'prioridad', 'categoria', 'es_recurrente', 'columna_kanban']
    search_fields = ['titulo', 'descripcion', 'etiquetas']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    inlines = [AsignacionInline, ComentarioInline]
    
    readonly_fields = ['fecha_completada', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información', {
            'fields': ('titulo', 'descripcion', 'categoria', 'etiquetas')
        }),
        ('Estado', {
            'fields': ('prioridad', 'estado', 'columna_kanban', 'porcentaje_completado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_vencimiento', 'fecha_completada')
        }),
        ('Jerarquía', {
            'fields': ('tarea_padre', 'orden_subtarea'),
            'classes': ('collapse',)
        }),
        ('Recurrencia', {
            'fields': ('es_recurrente', 'patron_recurrencia', 'intervalo_recurrencia', 'recurrencia_activa'),
            'classes': ('collapse',)
        }),
        ('Vinculación', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creador', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AsignacionTarea)
class AsignacionTareaAdmin(admin.ModelAdmin):
    """Admin para asignaciones"""
    list_display = ['tarea', 'usuario', 'rol', 'asignado_por', 'notificado']
    list_filter = ['rol', 'notificado']
    search_fields = ['tarea__titulo', 'usuario__username']


@admin.register(ComentarioTarea)
class ComentarioTareaAdmin(admin.ModelAdmin):
    """Admin para comentarios"""
    list_display = ['tarea', 'autor', 'contenido_corto', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tarea__titulo', 'contenido']
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Contenido'


@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    """Admin para archivos"""
    list_display = ['tarea', 'nombre', 'subido_por', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tarea__titulo', 'nombre']


@admin.register(RecordatorioTarea)
class RecordatorioTareaAdmin(admin.ModelAdmin):
    """Admin para recordatorios"""
    list_display = ['tarea', 'usuario', 'tipo', 'fecha_recordatorio', 'enviado']
    list_filter = ['tipo', 'enviado']
    search_fields = ['tarea__titulo']


@admin.register(HistorialTarea)
class HistorialTareaAdmin(admin.ModelAdmin):
    """Admin para historial"""
    list_display = ['tarea', 'usuario', 'accion', 'created_at']
    list_filter = ['accion', 'created_at']
    search_fields = ['tarea__titulo', 'descripcion']
    readonly_fields = ['tarea', 'usuario', 'accion', 'descripcion', 'datos_anteriores', 'datos_nuevos', 'created_at']
