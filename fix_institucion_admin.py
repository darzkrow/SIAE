"""
Script para arreglar admin de institucion
"""

# Leer el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Arreglar AlmacenRegionalAdmin - cambiar 'codigo' por 'prefijo'
content = content.replace(
    "class AlmacenRegionalAdmin(admin.ModelAdmin):\n    list_display = ['codigo', 'nombre', 'unidad_organizacional', 'activo']",
    "class AlmacenRegionalAdmin(admin.ModelAdmin):\n    list_display = ['prefijo', 'nombre', 'unidad_organizacional', 'activo']"
)
content = content.replace(
    "search_fields = ['nombre', 'codigo']",
    "search_fields = ['nombre', 'prefijo']",
    1  # Solo la primera ocurrencia (AlmacenRegional)
)

# Arreglar AprobacionTrasladoAdmin - cambiar 'fecha_aprobacion' por 'fecha_decision'
content = content.replace(
    "list_display = ['solicitud', 'tipo_aprobacion', 'aprobador', 'decision', 'fecha_aprobacion']",
    "list_display = ['solicitud', 'tipo_aprobacion', 'aprobador', 'decision', 'fecha_decision']"
)

# Arreglar OrganizacionCentralAdmin - remover 'codigo'
content = content.replace(
    "@admin.register(OrganizacionCentral)\nclass OrganizacionCentralAdmin(admin.ModelAdmin):\n    list_display = ['codigo', 'nombre']",
    "@admin.register(OrganizacionCentral)\nclass OrganizacionCentralAdmin(admin.ModelAdmin):\n    list_display = ['nombre', 'rif']"
)
content = content.replace(
    "class OrganizacionCentralAdmin(admin.ModelAdmin):\n    search_fields = ['nombre', 'codigo']",
    "class OrganizacionCentralAdmin(admin.ModelAdmin):\n    search_fields = ['nombre', 'rif']"
)

# Guardar el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Admin de institucion arreglado")
print("   - AlmacenRegionalAdmin: codigo → prefijo")
print("   - AprobacionTrasladoAdmin: fecha_aprobacion → fecha_decision")
print("   - OrganizacionCentralAdmin: removido 'codigo', agregado 'rif'")
