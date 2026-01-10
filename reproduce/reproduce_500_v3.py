
import os
import django
from decimal import Decimal
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import ChemicalProduct, Category, UnitOfMeasure, Supplier, Pipe, PumpAndMotor, Accessory
from inventario.serializers import (
    ChemicalProductSerializer, CategorySerializer, UnitOfMeasureSerializer, 
    SupplierSerializer, PipeSerializer, PumpAndMotorSerializer, AccessorySerializer
)

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

    # 5. Pipe
    try:
        pipe, _ = Pipe.objects.get_or_create(
            sku="PIPE-SER-001",
            defaults={
                'nombre': "Pipe Test",
                'categoria': cat,
                'unidad_medida': uom,
                'proveedor': prov,
                'material': 'PVC',
                'diametro_nominal': Decimal("2.0"),
                'unidad_diametro': 'PULGADAS'
            }
        )
        print(f"Testing Pipe: {pipe}")
        data = PipeSerializer(pipe).data
        print("✅ Pipe OK")
    except Exception as e:
        print(f"❌ Pipe ERROR: {e}")

    # 6. Pump
    try:
        pump, _ = PumpAndMotor.objects.get_or_create(
            sku="PUMP-SER-001",
            defaults={
                'nombre': "Pump Test",
                'categoria': cat,
                'unidad_medida': uom,
                'proveedor': prov,
                'tipo_equipo': 'BOMBA_CENTRIFUGA',
                'potencia_hp': Decimal("5.0")
            }
        )
        print(f"Testing Pump: {pump}")
        data = PumpAndMotorSerializer(pump).data
        print("✅ Pump OK")
    except Exception as e:
        print(f"❌ Pump ERROR: {e}")

    # 7. Accessory
    try:
        acc, _ = Accessory.objects.get_or_create(
            sku="ACC-SER-001",
            defaults={
                'nombre': "Accessory Test",
                'categoria': cat,
                'unidad_medida': uom,
                'proveedor': prov,
                'tipo_accesorio': 'CODO'
            }
        )
        print(f"Testing Accessory: {acc}")
        data = AccessorySerializer(acc).data
        print("✅ Accessory OK")
    except Exception as e:
        print(f"❌ Accessory ERROR: {e}")

if __name__ == '__main__':
    test_serializers()

if __name__ == '__main__':
    test_serializers()
