import os
import django
import sys
import uuid

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import MovimientoInventario, Pipe, Acueducto, Sucursal, OrganizacionCentral, Category, UnitOfMeasure, Supplier, InventoryAudit
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def run_reproduction():
    unique_suffix = str(uuid.uuid4())[:8]
    print(f"Testing MovimientoInventario creation with suffix {unique_suffix}...")
    
    # 1. Setup base data
    org, _ = OrganizacionCentral.objects.get_or_create(nombre=f"Org Test {unique_suffix}")
    suc, _ = Sucursal.objects.get_or_create(nombre=f"Suc Test {unique_suffix}", organizacion_central=org)
    acu, _ = Acueducto.objects.get_or_create(nombre=f"Acu Test {unique_suffix}", sucursal=suc)
    user, _ = User.objects.get_or_create(username=f"user_{unique_suffix}")
    
    cat = Category.objects.create(nombre=f"Cat {unique_suffix}", codigo=f"C{unique_suffix}")
    unit = UnitOfMeasure.objects.create(nombre=f"Unit {unique_suffix}", simbolo=f"u{unique_suffix}")
    sup, _ = Supplier.objects.get_or_create(nombre=f"Sup {unique_suffix}")
    
    # 2. Create a pipe
    pipe = Pipe(
        sku=f"SKU-{unique_suffix}",
        nombre=f"Tuberia {unique_suffix}",
        material="PVC",
        diametro_nominal=Decimal('100.00'),
        presion_nominal="PN10",
        tipo_union="ROSCADA",
        tipo_uso="POTABLE",
        longitud_unitaria=Decimal('6.00'),
        categoria=cat,
        unidad_medida=unit,
        proveedor=sup,
        stock_actual=Decimal('100.000'),
        stock_minimo=Decimal('10.000'),
        precio_unitario=Decimal('5.00')
    )
    pipe.presion_psi = Decimal('145.04') 
    pipe.save()

    ct = ContentType.objects.get_for_model(Pipe)
    
    try:
        # Create movement
        print("Attempting to save movement...")
        mov = MovimientoInventario(
            tipo_movimiento='ENTRADA',
            cantidad=Decimal('10.000'),
            content_type=ct,
            object_id=pipe.id,
            acueducto_destino=acu,
            creado_por=user,
            razon="Test failure"
        )
        mov.save()
        print("Movement created successfully!")
    except Exception as e:
        print(f"Error caught: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_reproduction()
