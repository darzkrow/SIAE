from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from geography.models import State, Municipality, Parish, Ubicacion
from stock.models import Stock

class StockInline(GenericTabularInline):
    model = Stock
    extra = 0
    fields = ['content_type', 'object_id', 'cantidad', 'lote', 'estado_operativo']
    readonly_fields = ['content_type', 'object_id', 'cantidad', 'lote']

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state']
    search_fields = ['name']
    list_filter = ['state']

@admin.register(Parish)
class ParishAdmin(admin.ModelAdmin):
    list_display = ['name', 'municipality']
    search_fields = ['name']
    list_filter = ['municipality__state']

@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'almacen_regional', 'subalmacen', 'acueducto', 'activa']
    list_filter = ['tipo', 'activa']
    search_fields = ['nombre']
    autocomplete_fields = ['parish', 'acueducto', 'almacen_regional', 'subalmacen']
    inlines = [StockInline]
