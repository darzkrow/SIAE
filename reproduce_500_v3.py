
import os
import django
from decimal import Decimal
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import ChemicalProduct, Category, UnitOfMeasure, Supplier
from inventario.serializers import ChemicalProductSerializer, CategorySerializer, UnitOfMeasureSerializer, SupplierSerializer

def test_serializers():
    print("--- INICIANDO TEST DE SERIALIZERS ---")

    # 1. Category
    try:
        cat, _ = Category.objects.get_or_create(
            nombre="Cat Test Serializer", 
            defaults={'codigo': "CTSER"}
        )
        print(f"Testing Category: {cat}")
        data = CategorySerializer(cat).data
        print("✅ Category OK")
    except Exception as e:
        print(f"❌ Category ERROR: {e}")

    # 2. Unit
    try:
        uom, _ = UnitOfMeasure.objects.get_or_create(
            nombre="Unit Test Serializer",
            defaults={'simbolo': "uts", 'tipo': 'UNIDAD'}
        )
        print(f"Testing Unit: {uom}")
        data = UnitOfMeasureSerializer(uom).data
        print("✅ Unit OK")
    except Exception as e:
        print(f"❌ Unit ERROR: {e}")

    # 3. Supplier
    try:
        prov, _ = Supplier.objects.get_or_create(
            nombre="Prov Test Serializer",
            defaults={'rif': 'J-999999-9', 'codigo': 'PTS'}
        )
        print(f"Testing Supplier: {prov}")
        data = SupplierSerializer(prov).data
        print("✅ Supplier OK")
    except Exception as e:
        print(f"❌ Supplier ERROR: {e}")

    # 4. Chemical
    try:
        # Create dependencies if needed
        # We reuse cat, uom, prov from above
        chem, _ = ChemicalProduct.objects.get_or_create(
            sku="CHEM-SER-001",
            defaults={
                'nombre': "Chemical Test",
                'categoria': cat,
                'unidad_medida': uom,
                'proveedor': prov,
                'precio_unitario': Decimal("50.00"),
                'stock_actual': Decimal("100.000"),
                'stock_minimo': Decimal("10.000"),
                'es_peligroso': False
            }
        )
        print(f"Testing Chemical: {chem}")
        data = ChemicalProductSerializer(chem).data
        print("✅ Chemical OK")
    except Exception as e:
        print(f"❌ Chemical ERROR: {e}")

if __name__ == '__main__':
    test_serializers()
