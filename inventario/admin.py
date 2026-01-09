from django.contrib import admin
from . import models

# ===========================================================================
# MODELOS ORGANIZACIONALES
# ===========================================================================

@admin.register(models.OrganizacionCentral)
class OrganizacionCentralAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rif']
    search_fields = ['nombre', 'rif']

@admin.register(models.Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'organizacion_central', 'codigo']
    list_filter = ['organizacion_central']
    search_fields = ['nombre', 'codigo']

@admin.register(models.Acueducto)
class AcueductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sucursal', 'codigo']
    list_filter = ['sucursal']
    search_fields = ['nombre', 'codigo']


# ===========================================================================
# MODELOS AUXILIARES
# ===========================================================================

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'activo', 'orden']
    list_filter = ['activo']
    search_fields = ['nombre', 'codigo']
    ordering = ['orden', 'nombre']

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
    list_display = ['producto', 'acueducto', 'cantidad', 'lote']
    list_filter = ['acueducto']
    search_fields = ['producto__nombre', 'lote']

@admin.register(models.StockPipe)
class StockPipeAdmin(admin.ModelAdmin):
    list_display = ['producto', 'acueducto', 'cantidad', 'metros_totales']
    list_filter = ['acueducto']
    search_fields = ['producto__nombre']
    readonly_fields = ['metros_totales']

@admin.register(models.StockPumpAndMotor)
class StockPumpAndMotorAdmin(admin.ModelAdmin):
    list_display = ['producto', 'acueducto', 'cantidad', 'estado_operativo']
    list_filter = ['acueducto', 'estado_operativo']
    search_fields = ['producto__numero_serie']

@admin.register(models.StockAccessory)
class StockAccessoryAdmin(admin.ModelAdmin):
    list_display = ['producto', 'acueducto', 'cantidad']
    list_filter = ['acueducto']
    search_fields = ['producto__nombre']
