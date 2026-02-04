"""
Script para agregar Subalmacén al admin
"""

# Leer el archivo admin.py
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar import de Subalmacen
if "Subalmacen" not in content:
    content = content.replace(
        "from .models import (",
        "from .models import (\n    Subalmacen,"
    )

# Admin de Subalmacén
subalmacen_admin = '''

@admin.register(Subalmacen)
class SubalmacenAdmin(admin.ModelAdmin):
    """Admin para Subalmacén"""
    list_display = ['codigo', 'nombre', 'sucursal', 'estado', 'municipio', 'responsable', 'activo']
    list_filter = ['activo', 'estado', 'municipio', 'sucursal']
    search_fields = ['nombre', 'codigo', 'direccion']
    ordering = ['estado__name', 'sucursal__nombre', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'sucursal', 'activo')
        }),
        ('Ubicación Geográfica', {
            'fields': ('estado', 'municipio', 'parroquia', 'direccion', 'coordenadas_gps')
        }),
        ('Gestión', {
            'fields': ('responsable', 'capacidad', 'descripcion')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'sucursal', 'estado', 'municipio', 'parroquia', 'responsable'
        )

'''

# Agregar antes del final del archivo
if "@admin.register(Subalmacen)" not in content:
    # Agregar al final del archivo
    content = content.rstrip() + "\n" + subalmacen_admin + "\n"

# Guardar el archivo modificado
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ SubalmacenAdmin agregado al admin")
