"""
Script para arreglar create_test_subalmacenes.py
"""

# Leer el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\create_test_subalmacenes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar la línea problemática
content = content.replace(
    "    org, created = OrganizacionCentral.objects.get_or_create(\n        nombre='Hidroven',\n        defaults={'codigo': 'HV-001'}\n    )",
    "    org, created = OrganizacionCentral.objects.get_or_create(\n        nombre='Hidroven',\n        defaults={'rif': 'J-00000000-0'}  # Changed from codigo to rif\n    )"
)

# Guardar el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\create_test_subalmacenes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Script arreglado: codigo → rif en OrganizacionCentral")
