from django.contrib import admin
from stock.models import Stock, MovimientoInventario, InventoryAudit

class InventoryAuditInline(admin.TabularInline):
    model = InventoryAudit
    extra = 0
    readonly_fields = [
        'status', 'tipo_movimiento', 'cantidad', 
        'ubicacion_origen', 'ubicacion_destino', 'user', 'fecha', 'mensaje'
    ]
    can_delete = False

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ubicacion', 'cantidad', 'estado_operativo', 'lote']
    list_filter = ['ubicacion', 'estado_operativo', 'fecha_vencimiento']
    search_fields = ['lote', 'object_id']
    readonly_fields = ['content_type', 'object_id']

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_movimiento', 'status', 'cantidad', 'ubicacion_origen', 'ubicacion_destino', 'fecha_movimiento']
    list_filter = ['tipo_movimiento', 'status', 'fecha_movimiento']
    search_fields = ['razon', 'object_id']
    readonly_fields = ['fecha_movimiento', 'creado_por']
    inlines = [InventoryAuditInline]

@admin.register(InventoryAudit)
class InventoryAuditAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'tipo_movimiento', 'cantidad', 'user', 'fecha']
    list_filter = ['status', 'tipo_movimiento', 'fecha']
    search_fields = ['mensaje']
    readonly_fields = [
        'movimiento', 'content_type', 'object_id', 'tipo_movimiento', 
        'cantidad', 'ubicacion_origen', 'ubicacion_destino', 'user', 
        'status', 'mensaje', 'fecha'
    ]
