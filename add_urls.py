"""
Script para agregar rutas de Subalmacén a urls.py
"""

# Leer el archivo urls.py
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar ruta de subalmacenes
subalmacen_route = "router.register(r'subalmacenes', views.SubalmacenViewSet, basename='subalmacen')\n"

# Buscar donde están las otras rutas del router y agregar
if "subalmacenes" not in content:
    # Buscar la línea de solicitudes-traslado y agregar después
    content = content.replace(
        "router.register(r'solicitudes-traslado', views.SolicitudTrasladoViewSet, basename='solicitud-traslado')",
        "router.register(r'solicitudes-traslado', views.SolicitudTrasladoViewSet, basename='solicitud-traslado')\n" + subalmacen_route
    )

# Guardar el archivo modificado
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\urls.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Ruta de subalmacenes agregada a urls.py")
