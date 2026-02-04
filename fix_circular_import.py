"""
Script para arreglar el import circular en geography/models.py
"""

# Leer el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\geography\models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover el import de Acueducto
content = content.replace(
    "from django.db import models\nfrom institucion.models import Acueducto",
    "from django.db import models"
)

# Cambiar el ForeignKey a usar string reference
content = content.replace(
    "    acueducto = models.ForeignKey(\n        Acueducto,",
    "    acueducto = models.ForeignKey(\n        'institucion.Acueducto',  # String reference to avoid circular import"
)

# Guardar el archivo
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\geography\models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Import circular arreglado en geography/models.py")
print("   - Removido: from institucion.models import Acueducto")
print("   - Cambiado FK a: 'institucion.Acueducto' (string reference)")
