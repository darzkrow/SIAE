from django.contrib import admin
from . import models


@admin.register(models.OrganizacionCentral)
class OrganizacionCentralAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rif')


@admin.register(models.Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'organizacion_central')
    list_filter = ('organizacion_central',)


@admin.register(models.Acueducto)
class AcueductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sucursal')
    list_filter = ('sucursal',)


@admin.register(models.Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


@admin.register(models.Tuberia)
class TuberiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'material', 'diametro_nominal_mm', 'longitud_m')
    list_filter = ('categoria', 'material')


@admin.register(models.Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'marca', 'modelo', 'numero_serie')
    search_fields = ('numero_serie', 'nombre', 'marca')




@admin.register(models.StockTuberia)
class StockTuberiaAdmin(admin.ModelAdmin):
    list_display = ('tuberia', 'acueducto', 'cantidad', 'fecha_ultima_actualizacion')
    list_filter = ('acueducto', 'tuberia')


@admin.register(models.StockEquipo)
class StockEquipoAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'acueducto', 'cantidad', 'fecha_ultima_actualizacion')
    list_filter = ('acueducto', 'equipo')


@admin.register(models.InventoryAudit)
class InventoryAuditAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'status', 'tipo_movimiento', 'articulo_nombre')
    list_filter = ('status', 'tipo_movimiento')
    readonly_fields = ('fecha',)


@admin.register(models.AlertaStock)
class AlertaStockAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'acueducto', 'umbral_minimo', 'activo', 'creado_en')
    list_filter = ('acueducto', 'activo')
    search_fields = ('tuberia__nombre', 'equipo__nombre')


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('creada_en', 'enviada', 'enviada_en', 'mensaje')
    readonly_fields = ('creada_en', 'enviada_en')


@admin.register(models.MovimientoInventario)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('tipo_movimiento', 'get_articulo_display', 'cantidad', 'fecha_movimiento')
    list_filter = ('tipo_movimiento', 'fecha_movimiento')

    def get_articulo_display(self, obj):
        return obj.get_articulo_display_name()
    get_articulo_display.short_description = 'Artículo'
