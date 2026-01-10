
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import ChemicalProduct, MovimientoInventario, StockChemical, Category, UnitOfMeasure, Supplier, Acueducto, Sucursal, OrganizacionCentral, Alerta
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

def run_check():
    print("--- INICIANDO VERIFICACION V2 ---")
    
    # 1. Asegurar dependencias
    org, _ = OrganizacionCentral.objects.get_or_create(nombre="Org Test")
    suc, _ = Sucursal.objects.get_or_create(nombre="Suc Test", organizacion_central=org)
    acu, _ = Acueducto.objects.get_or_create(nombre="Acu Test", sucursal=suc)
    
    cat, _ = Category.objects.get_or_create(nombre="Quimicos V2", codigo="QTEST")
    uom, _ = UnitOfMeasure.objects.get_or_create(simbolo="kg", defaults={'nombre': "Kg", 'tipo': "PESO"})
    prov, _ = Supplier.objects.get_or_create(nombre="Prov Test")

    User = get_user_model()
    user = User.objects.first()
    if not user:
        print("No user found, creating admin")
        user = User.objects.create_superuser('admin_v2', 'admin@example.com', 'admin')

    # 2. Crear Producto
    chem, created = ChemicalProduct.objects.get_or_create(
        sku="QTEST-001",
        defaults={
            'nombre': "Cloro Test",
            'categoria': cat,
            'unidad_medida': uom,
            'proveedor': prov,
            'precio_unitario': Decimal("10.50"),
            'stock_minimo': Decimal("100"),
            'es_peligroso': True,
            'nivel_peligrosidad': 'ALTO'
        }
    )
    print(f"Producto: {chem} (Creado: {created})")

    # 3. Crear Movimiento (Entrada)
    print("Creando movimiento de entrada...")
    mov = MovimientoInventario.objects.create(
        content_type=ContentType.objects.get_for_model(chem),
        object_id=chem.id,
        tipo_movimiento='ENTRADA',
        cantidad=Decimal("500"),
        acueducto_destino=acu,
        creado_por=user,
        razon="Test Entrada Script"
    )
    print(f"Movimiento generado: {mov}")
    
    # 4. Verificar Stock
    stock = StockChemical.objects.get(producto=chem, acueducto=acu)
    print(f"Stock actual en {acu}: {stock.cantidad}")
    
    if stock.cantidad >= 500:
        print("✅ Stock actualizado correctamente.")
    else:
        print("❌ ERROR: Stock no actualizado.")

    # 5. Crear Alerta
    alert, created = Alerta.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(chem),
        object_id=chem.id,
        acueducto=acu,
        defaults={'umbral_minimo': 50}
    )
    print(f"Alerta creada: {alert}")
    
    # 6. Serializers Check (Simulado)
    from inventario.serializers import AlertaSerializer
    ser = AlertaSerializer(alert)
    print(f"Serializer data partial: product_type={ser.data.get('product_type', 'N/A')}")
    
    print("--- VERIFICACION COMPLETADA EXITOSAMENTE ---")

if __name__ == '__main__':
    try:
        run_check()
    except Exception as e:
        print(f"❌ FALLO VERIFICACION: {e}")
        import traceback
        traceback.print_exc()
