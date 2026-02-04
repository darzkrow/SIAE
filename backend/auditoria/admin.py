from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'user', 'action', 'object_repr', 
        'ip_address', 'risk_level', 'changes_summary'
    ]
    list_filter = [
        'action', 'risk_level', 'timestamp', 'content_type'
    ]
    search_fields = [
        'object_repr', 'user__username', 'user__email',
        'ip_address', 'changes', 'extra_data'
    ]
    readonly_fields = [f.name for f in AuditLog._meta.fields] + ['changes_display', 'extra_data_display']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('timestamp', 'user', 'action', 'risk_level')
        }),
        ('Objeto Afectado', {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        ('Cambios Realizados', {
            'fields': ('changes_display', 'changes')
        }),
        ('Información de Solicitud', {
            'fields': ('ip_address', 'user_agent', 'session_key')
        }),
        ('Datos Adicionales', {
            'fields': ('extra_data_display', 'extra_data'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def changes_summary(self, obj):
        """Display a short summary of changes in the list view."""
        summary = obj.get_changes_summary()
        if len(summary) > 50:
            return summary[:47] + "..."
        return summary
    changes_summary.short_description = 'Resumen de Cambios'
    
    def changes_display(self, obj):
        """Display formatted changes in the detail view."""
        if not obj.changes:
            return "Sin cambios registrados"
        
        try:
            formatted = json.dumps(obj.changes, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>', formatted)
        except (TypeError, ValueError):
            return str(obj.changes)
    changes_display.short_description = 'Cambios (Formateado)'
    
    def extra_data_display(self, obj):
        """Display formatted extra data in the detail view."""
        if not obj.extra_data:
            return "Sin datos adicionales"
        
        try:
            formatted = json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>', formatted)
        except (TypeError, ValueError):
            return str(obj.extra_data)
    extra_data_display.short_description = 'Datos Adicionales (Formateado)'
