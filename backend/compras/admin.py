from django.contrib import admin
from .models import OrdenCompra, ItemOrden, Correlativo

class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 1

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'status', 'solicitante', 'fecha_creacion']
    list_filter = ['status']
    search_fields = ['codigo', 'notas']
    inlines = [ItemOrdenInline]

@admin.register(Correlativo)
class CorrelativoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'prefijo', 'ultimo_numero', 'anio']
