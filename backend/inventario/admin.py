from django.contrib import admin
from . import models

# ===========================================================================
# MODELOS AUXILIARES
# ===========================================================================

# Categoría y Marca se administran en la app 'catalogo'

@admin.register(models.UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'simbolo', 'tipo', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'simbolo']

@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rif', 'codigo', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rif', 'codigo', 'email']


# ===========================================================================
# PRODUCTOS
# ===========================================================================

@admin.register(models.ChemicalProduct)
class ChemicalProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'es_peligroso', 'stock_actual', 'activo']
    list_filter = ['categoria', 'es_peligroso', 'nivel_peligrosidad', 'presentacion', 'activo']
    search_fields = ['sku', 'nombre', 'numero_un']
    readonly_fields = ['sku', 'creado_en', 'actualizado_en']

@admin.register(models.Pipe)
class PipeAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'material', 'diametro_nominal', 'stock_actual']
    list_filter = ['categoria', 'material', 'tipo_uso', 'activo']
    search_fields = ['sku', 'nombre']
    readonly_fields = ['sku', 'presion_psi', 'creado_en', 'actualizado_en']

@admin.register(models.PumpAndMotor)
class PumpAndMotorAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'tipo_equipo', 'marca', 'potencia_hp']
    list_filter = ['categoria', 'tipo_equipo', 'marca', 'activo']
    search_fields = ['sku', 'nombre', 'numero_serie']
    readonly_fields = ['sku', 'potencia_kw', 'creado_en', 'actualizado_en']

@admin.register(models.Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'tipo_accesorio', 'tipo_conexion']
    list_filter = ['categoria', 'tipo_accesorio', 'tipo_conexion', 'activo']
    search_fields = ['sku', 'nombre']
    readonly_fields = ['sku', 'creado_en', 'actualizado_en']


# ===========================================================================
# STOCK
# ===========================================================================

@admin.register(models.StockChemical)
class StockChemicalAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ubicacion', 'cantidad', 'lote']
    list_filter = ['ubicacion']
    search_fields = ['producto__nombre', 'lote']

@admin.register(models.StockPipe)
class StockPipeAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ubicacion', 'cantidad', 'metros_totales']
    list_filter = ['ubicacion']
    search_fields = ['producto__nombre']
    readonly_fields = ['metros_totales']

@admin.register(models.StockPumpAndMotor)
class StockPumpAndMotorAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ubicacion', 'cantidad', 'estado_operativo']
    list_filter = ['ubicacion', 'estado_operativo']
    search_fields = ['producto__numero_serie']

@admin.register(models.StockAccessory)
class StockAccessoryAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ubicacion', 'cantidad']
    list_filter = ['ubicacion']
    search_fields = ['producto__nombre']


# ===========================================================================
# MOVIMIENTOS Y AUDITORÍA
# ===========================================================================

@admin.register(models.MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_movimiento', 'status', 'cantidad', 'ubicacion_origen', 'ubicacion_destino', 'fecha_movimiento']
    list_filter = ['tipo_movimiento', 'status', 'fecha_movimiento']
    search_fields = ['razon']
    readonly_fields = ['fecha_movimiento', 'creado_por']

@admin.register(models.InventoryAudit)
class InventoryAuditAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'tipo_movimiento', 'cantidad', 'user', 'fecha']
    list_filter = ['status', 'tipo_movimiento', 'fecha']
    search_fields = ['mensaje']
    readonly_fields = ['movimiento', 'content_type', 'object_id', 'tipo_movimiento', 'cantidad', 'ubicacion_origen', 'ubicacion_destino', 'user', 'status', 'mensaje', 'fecha']
