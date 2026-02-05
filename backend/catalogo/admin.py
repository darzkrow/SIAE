from django.contrib import admin
from catalogo.models import CategoriaProducto, Marca, Tag

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'activo', 'orden']
    search_fields = ['nombre', 'codigo']
    list_filter = ['activo']

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    search_fields = ['nombre']
    list_filter = ['activo']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']
