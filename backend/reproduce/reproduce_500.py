
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import Acueducto, Sucursal, OrganizacionCentral, MovimientoInventario, ChemicalProduct, Category, UnitOfMeasure, Supplier
from inventario.serializers import AcueductoSerializer, MovimientoInventarioSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

def test_acueducto_serialization():
    print("Testing Acueducto Serialization...")
    try:
        org, _ = OrganizacionCentral.objects.get_or_create(nombre="Org Debug", defaults={'rif': 'J-00000000-0'})
        suc, _ = Sucursal.objects.get_or_create(nombre="Suc Debug", defaults={'organizacion_central': org, 'codigo': 'SUC-DBG'})
        acu, _ = Acueducto.objects.get_or_create(nombre="Acu Debug", defaults={'sucursal': suc, 'codigo': 'ACU-DBG'})
        
        serializer = AcueductoSerializer(acu)
        data = serializer.data
        print(f"✅ Acueducto serialized: {data['nombre']}")
    except Exception as e:
        print(f"❌ Acueducto Serialization Failed: {e}")
        import traceback
        traceback.print_exc()

def test_movimiento_serialization_null_user():
    print("\nTesting Movimiento Serialization (Null User)...")
    try:
        # Fixtures
        cat, _ = Category.objects.get_or_create(nombre="Cat Debug", defaults={'codigo': "CDBG"})
        uom, _ = UnitOfMeasure.objects.get_or_create(simbolo="db", defaults={'nombre': "Debug", 'tipo': "UNIDAD"})
        prov, _ = Supplier.objects.get_or_create(nombre="Prov Debug", defaults={'rif': 'J-12345678-9', 'codigo': 'PROV-DBG'})
        chem, _ = ChemicalProduct.objects.get_or_create(sku="DBG-001", defaults={'nombre': "Chem Debug", 'categoria': cat, 'unidad_medida': uom, 'proveedor': prov})
        
        org, _ = OrganizacionCentral.objects.get_or_create(nombre="Org Debug", defaults={'rif': 'J-00000000-0'})
        suc, _ = Sucursal.objects.get_or_create(nombre="Suc Debug", defaults={'organizacion_central': org, 'codigo': 'SUC-DBG'})
        acu, _ = Acueducto.objects.get_or_create(nombre="Acu Debug", defaults={'sucursal': suc, 'codigo': 'ACU-DBG'})

        # Create Movimiento with creado_por=None
        mov = MovimientoInventario.objects.create(
            content_type=ContentType.objects.get_for_model(chem),
            object_id=chem.id,
            tipo_movimiento='ENTRADA',
            cantidad=10,
            acueducto_destino=acu,
            creado_por=None # Explicitly None
        )
        
        serializer = MovimientoInventarioSerializer(mov)
        data = serializer.data
        print(f"✅ Movimiento serialized: {data['id']}")
    except Exception as e:
        print(f"❌ Movimiento Serialization Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_acueducto_serialization()
    test_movimiento_serialization_null_user()
