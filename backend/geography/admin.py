from django.contrib import admin
from .models import State, Municipality, Parish, Ubicacion


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state')


@admin.register(Parish)
class ParishAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'municipality')


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'parish', 'acueducto', 'activa')
    list_filter = ('tipo', 'activa', 'parish__municipality__state', 'acueducto__sucursal')
    search_fields = ('nombre', 'descripcion', 'acueducto__nombre', 'parish__name')
