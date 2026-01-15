from django.contrib import admin
from .models import OrganizacionCentral, Sucursal, Acueducto

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
