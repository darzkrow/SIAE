import os
import django
import sys
from decimal import Decimal

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import Pipe, Acueducto, Sucursal, OrganizacionCentral, Category, UnitOfMeasure, Supplier
from inventario.views import MovimientoInventarioViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

def run_test():
    print("Directly testing ViewSet.create with setup...")
    
    # Setup data
    org, _ = OrganizacionCentral.objects.get_or_create(nombre="Test Org V")
    suc, _ = Sucursal.objects.get_or_create(nombre="Test Suc V", defaults={'organizacion_central': org, 'codigo': 'TSV'})
    acu, _ = Acueducto.objects.get_or_create(nombre="Test Acu V", defaults={'sucursal': suc})
    user, _ = User.objects.get_or_create(username="testadminv", defaults={'is_staff': True})
    cat, _ = Category.objects.get_or_create(codigo='TUV', defaults={'nombre': 'Test Cat V'})
    unit, _ = UnitOfMeasure.objects.get_or_create(simbolo='uv', defaults={'nombre': 'Test Unit V'})
    sup, _ = Supplier.objects.get_or_create(nombre="Test Sup V")
    
    pipe, _ = Pipe.objects.get_or_create(
        sku="TEST-PIPE-V",
        defaults={
            'nombre': 'Pipe V',
            'material': 'PVC',
            'diametro_nominal': Decimal('10.00'),
            'presion_nominal': 'PN10',
            'tipo_union': 'ROSCADA',
            'tipo_uso': 'POTABLE',
            'categoria': cat,
            'unidad_medida': unit,
            'proveedor': sup,
            'stock_actual': Decimal('0'),
            'stock_minimo': Decimal('1'),
            'precio_unitario': Decimal('10')
        }
    )

    factory = APIRequestFactory()
    data = {
        'tipo_movimiento': 'ENTRADA',
        'cantidad': 1,
        'product_type': 'pipe',
        'product_id': pipe.id,
        'acueducto_destino': acu.id,
        'razon': 'Direct ViewSet Test'
    }
    
    request = factory.post('/api/movimientos/', data, format='json')
    force_authenticate(request, user=user)
    
    view = MovimientoInventarioViewSet.as_view({'post': 'create'})
    
    try:
        response = view(request)
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"CRASH in ViewSet: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
