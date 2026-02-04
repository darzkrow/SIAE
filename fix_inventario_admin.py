"""
Script para arreglar campos de timestamp en inventario/admin.py
"""

# Leer el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\inventario\admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar creado_en y actualizado_en por created_at y updated_at
content = content.replace("'creado_en'", "'created_at'")
content = content.replace("'actualizado_en'", "'updated_at'")

# Guardar el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\inventario\admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Campos de timestamp arreglados en inventario/admin.py")
print("   - creado_en → created_at")
print("   - actualizado_en → updated_at")
