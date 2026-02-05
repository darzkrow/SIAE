from django.contrib import admin
from proveedores.models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rif', 'codigo', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rif', 'codigo', 'email']
