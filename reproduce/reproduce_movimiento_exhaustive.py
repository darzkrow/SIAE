import os
import django
import sys
from decimal import Decimal

# Configurar Django para usar db_test.sqlite3
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import config.settings as base_settings
base_settings.DATABASES['default']['NAME'] = 'db_test.sqlite3'

django.setup()

from inventario.models import MovimientoInventario, Pipe, Acueducto, ChemicalProduct, PumpAndMotor, Accessory, InventoryAudit, StockPipe, StockChemical, StockPumpAndMotor, StockAccessory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

def test_combination(product, acu_dest, acu_orig, tipo, user):
    ct = ContentType.objects.get_for_model(product)
    print(f"\n--- Testing: {tipo} for {ct.model} ---")
    try:
        mov = MovimientoInventario(
            tipo_movimiento=tipo,
            cantidad=Decimal('1.000'),
            content_type=ct,
            object_id=product.id,
            acueducto_destino=acu_dest,
            acueducto_origen=acu_orig,
            creado_por=user,
            razon=f"Test {tipo} {ct.model}"
        )
        mov.save()
        print(f"SUCCESS: {tipo} {ct.model}")
    except Exception as e:
        print(f"FAILED: {tipo} {ct.model} -> {type(e).__name__}: {e}")
        # import traceback
        # traceback.print_exc()

def run_reproduction():
    user = User.objects.first()
    acu1 = Acueducto.objects.all()[0] if Acueducto.objects.count() > 0 else None
    acu2 = Acueducto.objects.all()[1] if Acueducto.objects.count() > 1 else acu1
    
    pipe = Pipe.objects.first()
    chem = ChemicalProduct.objects.first()
    pump = PumpAndMotor.objects.first()
    acc = Accessory.objects.first()

    products = [p for p in [pipe, chem, pump, acc] if p is not None]
    
    for p in products:
        test_combination(p, acu1, None, 'ENTRADA', user)
        test_combination(p, None, acu1, 'SALIDA', user)
        if acu1 != acu2:
            test_combination(p, acu2, acu1, 'TRANSFERENCIA', user)
        test_combination(p, acu1, None, 'AJUSTE', user)

if __name__ == "__main__":
    run_reproduction()
