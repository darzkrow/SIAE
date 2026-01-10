import os
import django
import sys
from decimal import Decimal

# Configurar Django para usar db_test.sqlite3
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Patch settings before setup
from django.conf import settings
if not settings.configured:
    # Trigger setting loading
    pass

# Update DATABASES setting
import config.settings as base_settings
base_settings.DATABASES['default']['NAME'] = 'db_test.sqlite3'

django.setup()

from inventario.models import MovimientoInventario, Pipe, Acueducto, ChemicalProduct, PumpAndMotor, Accessory, InventoryAudit
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

def run_reproduction():
    print("Testing MovimientoInventario creation on db_test.sqlite3...")
    
    # Try to find any existing data
    pipe = Pipe.objects.first()
    chem = ChemicalProduct.objects.first()
    acu = Acueducto.objects.first()
    user = User.objects.first()
    
    product = pipe or chem or PumpAndMotor.objects.first() or Accessory.objects.first()
    
    if not product:
        print("No products found in DB. Test cannot proceed.")
        return
    if not acu:
        print("No acueductos found in DB. Test cannot proceed.")
        return
    if not user:
        print("No users found in DB. Test cannot proceed.")
        return

    ct = ContentType.objects.get_for_model(product)
    
    print(f"Using product: {product} (ID: {product.id}, Type: {ct.model})")
    print(f"Using acueducto: {acu} (ID: {acu.id})")
    print(f"Using user: {user} (Username: {user.username})")

    try:
        # Create movement
        print(f"Attempting to save movement...")
        mov = MovimientoInventario(
            tipo_movimiento='ENTRADA',
            cantidad=Decimal('1.000'),
            content_type=ct,
            object_id=product.id,
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
