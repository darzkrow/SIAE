from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from stock.models import Stock
from productos.models import (
    UnitOfMeasure, ChemicalProduct, 
    Pipe, PumpAndMotor, Accessory
)
from proveedores.models import Supplier

class StockInline(GenericTabularInline):
    model = Stock
    extra = 0
    fields = ['ubicacion', 'cantidad', 'lote', 'estado_operativo']
    readonly_fields = ['ubicacion', 'cantidad', 'lote']

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'simbolo', 'tipo', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'simbolo']

# SupplierAdmin moved to proveedores app

@admin.register(ChemicalProduct)
class ChemicalProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'es_peligroso', 'stock_actual', 'activo']
    list_filter = ['categoria', 'es_peligroso', 'nivel_peligrosidad', 'presentacion', 'activo']
    search_fields = ['sku', 'nombre', 'numero_un']
    readonly_fields = ['sku', 'created_at', 'updated_at']
    inlines = [StockInline]
    autocomplete_fields = ['categoria', 'unidad_medida', 'proveedor']

@admin.register(Pipe)
class PipeAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'material', 'diametro_nominal', 'stock_actual']
    list_filter = ['categoria', 'material', 'tipo_uso', 'activo']
    search_fields = ['sku', 'nombre']
    readonly_fields = ['sku', 'presion_psi', 'created_at', 'updated_at']
    inlines = [StockInline]
    autocomplete_fields = ['categoria', 'unidad_medida', 'proveedor']

@admin.register(PumpAndMotor)
class PumpAndMotorAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'tipo_equipo', 'marca', 'potencia_hp']
    list_filter = ['categoria', 'tipo_equipo', 'marca', 'activo']
    search_fields = ['sku', 'nombre', 'numero_serie']
    readonly_fields = ['sku', 'potencia_kw', 'created_at', 'updated_at']
    inlines = [StockInline]
    autocomplete_fields = ['categoria', 'unidad_medida', 'proveedor', 'marca']

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nombre', 'tipo_accesorio', 'tipo_conexion']
    list_filter = ['categoria', 'tipo_accesorio', 'tipo_conexion', 'activo']
    search_fields = ['sku', 'nombre']
    readonly_fields = ['sku', 'created_at', 'updated_at']
    inlines = [StockInline]
    autocomplete_fields = ['categoria', 'unidad_medida', 'proveedor']
