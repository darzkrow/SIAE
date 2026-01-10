
import os
import django
from decimal import Decimal
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import ChemicalProduct, Category, UnitOfMeasure, Supplier
from inventario.serializers import ChemicalProductSerializer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

def test_chemical_put():
    print("--- TESTING CHEMICAL PUT (UPDATE) ---")
    try:
        # Get an existing chemical product or create one
        cat, _ = Category.objects.get_or_create(nombre="Cat Test", defaults={'codigo': "CT"})
        uom, _ = UnitOfMeasure.objects.get_or_create(nombre="Unit Test", defaults={'simbolo': "ut", 'tipo': 'UNIDAD'})
        prov, _ = Supplier.objects.get_or_create(nombre="Prov Test", defaults={'rif': 'J-123', 'codigo': 'PT'})
        
        chem, created = ChemicalProduct.objects.get_or_create(
            sku="CHEM-PUT-001",
            defaults={
                'nombre': "Chemical for PUT",
                'categoria': cat,
                'unidad_medida': uom,
                'proveedor': prov,
                'precio_unitario': Decimal("10.00"),
                'stock_actual': Decimal("50.000"),
                'stock_minimo': Decimal("5.000"),
            }
        )
        print(f"Product ID: {chem.id}, Created: {created}")

        # Data for update
        update_data = {
            'nombre': "Updated Chemical Name",
            'categoria': cat.id,
            'unidad_medida': uom.id,
            'proveedor': prov.id,
            'stock_actual': 55.0,
            'stock_minimo': 6.0,
            'precio_unitario': 11.0,
            'es_peligroso': False
        }

        serializer = ChemicalProductSerializer(chem, data=update_data, partial=True)
        if serializer.is_valid():
            print("Serializer is valid. Saving...")
            serializer.save()
            print("✅ Chemical update successful")
        else:
            print(f"❌ Serializer validation FAILED: {serializer.errors}")

    except Exception as e:
        print(f"❌ Chemical PUT ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_chemical_put()
