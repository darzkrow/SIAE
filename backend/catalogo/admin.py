from django.contrib import admin
from .models import CategoriaProducto, Marca

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'activo', 'orden']
    list_filter = ['activo']
    search_fields = ['nombre', 'codigo']
    ordering = ['orden', 'nombre']

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
