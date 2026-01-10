import os
import django
import sys
import uuid

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import MovimientoInventario, Pipe, Acueducto, Category, UnitOfMeasure, Supplier, InventoryAudit, Sucursal, OrganizacionCentral
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def run_reproduction():
    print("Testing MovimientoInventario creation with robust setup...")
    
    # 1. Setup base data reliably
    org, _ = OrganizacionCentral.objects.get_or_create(nombre="Test Org")
    suc, _ = Sucursal.objects.get_or_create(nombre="Test Suc", defaults={'organizacion_central': org})
    acu, _ = Acueducto.objects.get_or_create(nombre="Test Acu", defaults={'sucursal': suc})
    user, _ = User.objects.get_or_create(username="testadmin", defaults={'is_staff': True})
    
    cat, _ = Category.objects.get_or_create(codigo='QUI', defaults={'nombre': 'Quimicos'})
    unit, _ = UnitOfMeasure.objects.get_or_create(simbolo='kg', defaults={'nombre': 'Kilogramos'})
    sup, _ = Supplier.objects.get_or_create(nombre="Proveedor Test")
    
    pipe, _ = Pipe.objects.get_or_create(
        sku="TEST-PIPE-001",
        defaults={
            'nombre': 'Tuberia Test',
            'material': 'PVC',
            'diametro_nominal': Decimal('110.00'),
            'presion_nominal': 'PN10',
            'tipo_union': 'SOLDABLE',
            'tipo_uso': 'POTABLE',
            'categoria': cat,
            'unidad_medida': unit,
            'proveedor': sup,
            'stock_actual': Decimal('0'),
            'stock_minimo': Decimal('10'),
            'precio_unitario': Decimal('100.00')
        }
    )

    ct = ContentType.objects.get_for_model(Pipe)
    
    try:
        # Create movement
        print(f"Attempting to save movement for Pipe {pipe.id} and Acueducto {acu.id}...")
        mov = MovimientoInventario(
            tipo_movimiento='ENTRADA',
            cantidad=Decimal('5.000'),
            content_type=ct,
            object_id=pipe.id,
            acueducto_destino=acu,
            creado_por=user,
            razon="Internal Debug Test"
        )
        mov.save()
        print("Movement created successfully!")
    except Exception as e:
        print(f"Error caught: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_reproduction()
