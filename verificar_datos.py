#!/usr/bin/env python
"""
Script para verificar que los datos de prueba se cargaron correctamente
Uso: python manage.py shell < verificar_datos.py
"""
from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto, Categoria,
    Tuberia, Equipo, StockTuberia, StockEquipo,
    MovimientoInventario, AlertaStock, InventoryAudit
)
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*80)
print("✅ VERIFICACIÓN DE DATOS DE PRUEBA")
print("="*80 + "\n")

# Contar registros
print("📊 CONTEO DE REGISTROS:")
print("-" * 80)

org_count = OrganizacionCentral.objects.count()
print(f"  Organizaciones: {org_count} (esperado: 1)")

sucursal_count = Sucursal.objects.count()
print(f"  Sucursales: {sucursal_count} (esperado: 3)")

acueducto_count = Acueducto.objects.count()
print(f"  Acueductos: {acueducto_count} (esperado: 7)")

categoria_count = Categoria.objects.count()
print(f"  Categorías: {categoria_count} (esperado: 8)")

tuberia_count = Tuberia.objects.count()
print(f"  Tuberías: {tuberia_count} (esperado: 6)")

equipo_count = Equipo.objects.count()
print(f"  Equipos: {equipo_count} (esperado: 11)")

stock_tuberia_count = StockTuberia.objects.count()
print(f"  Stock Tuberías: {stock_tuberia_count} (esperado: 7)")

stock_equipo_count = StockEquipo.objects.count()
print(f"  Stock Equipos: {stock_equipo_count} (esperado: 11)")

alerta_count = AlertaStock.objects.count()
print(f"  Alertas: {alerta_count} (esperado: 4)")

user_count = User.objects.count()
print(f"  Usuarios: {user_count} (esperado: 3)")

# Detalles de sucursales
print("\n" + "="*80)
print("🏢 SUCURSALES:")
print("-" * 80)
for sucursal in Sucursal.objects.all():
    acueductos = sucursal.acueductos.count()
    print(f"  • {sucursal.nombre}")
    print(f"    └─ Acueductos: {acueductos}")

# Detalles de stock
print("\n" + "="*80)
print("📦 STOCK TOTAL:")
print("-" * 80)

total_tuberias = StockTuberia.objects.aggregate(
    total=__import__('django.db.models', fromlist=['Sum']).Sum('cantidad')
)['total'] or 0
print(f"  Tuberías: {total_tuberias} unidades")

total_equipos = StockEquipo.objects.aggregate(
    total=__import__('django.db.models', fromlist=['Sum']).Sum('cantidad')
)['total'] or 0
print(f"  Equipos: {total_equipos} unidades")

# Detalles de usuarios
print("\n" + "="*80)
print("👥 USUARIOS:")
print("-" * 80)
for user in User.objects.all():
    print(f"  • {user.username} ({user.role})")
    print(f"    └─ Email: {user.email}")

# Detalles de alertas
print("\n" + "="*80)
print("🚨 ALERTAS DE STOCK BAJO:")
print("-" * 80)
for alerta in AlertaStock.objects.all():
    articulo = alerta.tuberia or alerta.equipo
    print(f"  • {articulo}")
    print(f"    └─ Umbral: {alerta.umbral_minimo}")
    print(f"    └─ Acueducto: {alerta.acueducto}")

# Validaciones
print("\n" + "="*80)
print("✅ VALIDACIONES:")
print("-" * 80)

validaciones = [
    (org_count == 1, "Organización creada"),
    (sucursal_count == 3, "3 Sucursales creadas"),
    (acueducto_count == 7, "7 Acueductos creados"),
    (tuberia_count == 6, "6 Tuberías creadas"),
    (equipo_count == 11, "11 Equipos creados"),
    (stock_tuberia_count == 7, "7 Stocks de tuberías creados"),
    (stock_equipo_count == 11, "11 Stocks de equipos creados"),
    (alerta_count == 4, "4 Alertas creadas"),
    (user_count == 3, "3 Usuarios creados"),
]

for validacion, descripcion in validaciones:
    estado = "✅" if validacion else "❌"
    print(f"  {estado} {descripcion}")

# Resumen
print("\n" + "="*80)
print("📊 RESUMEN:")
print("-" * 80)
print(f"  Total de registros: {org_count + sucursal_count + acueducto_count + categoria_count + tuberia_count + equipo_count + stock_tuberia_count + stock_equipo_count + alerta_count + user_count}")
print(f"  Stock total: {total_tuberias + total_equipos} unidades")
print(f"  Validaciones: {sum(1 for v, _ in validaciones if v)}/{len(validaciones)}")

if all(v for v, _ in validaciones):
    print("\n✅ TODOS LOS DATOS SE CARGARON CORRECTAMENTE")
else:
    print("\n⚠️  ALGUNAS VALIDACIONES FALLARON")

print("\n" + "="*80 + "\n")
