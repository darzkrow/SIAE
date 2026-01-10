import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import (
    ChemicalProduct, Pipe, Acueducto, MovimientoInventario, 
    StockChemical, StockPipe, Category, UnitOfMeasure, 
    Supplier, OrganizacionCentral, Sucursal
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def run_exhaustive_tests():
    print("--- INICIANDO PRUEBAS EXHAUSTIVAS DE MOVIMIENTOS ---")
    
    # 0. SETUP DATA
    admin_user, _ = User.objects.get_or_create(username="tester_admin", defaults={'role': 'ADMIN', 'is_staff': True})
    org, _ = OrganizacionCentral.objects.get_or_create(nombre="Corporacion de Prueba", defaults={'rif': "J-00000000"})
    suc, _ = Sucursal.objects.get_or_create(nombre="Sucursal Central de Pruebas", defaults={'organizacion_central': org})
    acu1, _ = Acueducto.objects.get_or_create(nombre="Acueducto Norte (Prueba)", defaults={'sucursal': suc})
    acu2, _ = Acueducto.objects.get_or_create(nombre="Acueducto Sur (Prueba)", defaults={'sucursal': suc})
    
    cat_q, _ = Category.objects.get_or_create(nombre="Quimicos Test", defaults={'codigo': 'Q-TEST'})
    cat_t, _ = Category.objects.get_or_create(nombre="Tuberias Test", defaults={'codigo': 'T-TEST'})
    uom_kg, _ = UnitOfMeasure.objects.get_or_create(simbolo="kg-ex", defaults={'nombre': "Kilogramos Exhaustivo", 'tipo': 'PESO'})
    uom_m, _ = UnitOfMeasure.objects.get_or_create(simbolo="m-ex", defaults={'nombre': "Metros Exhaustivo", 'tipo': 'LONGITUD'})
    sup, _ = Supplier.objects.get_or_create(nombre="Proveedor Global", defaults={'rif': "J-GLOBAL"})

    # Productos
    cloro, _ = ChemicalProduct.objects.get_or_create(
        sku="CHEM-TEST-001",
        defaults={
            'nombre': "Cloro de Prueba",
            'categoria': cat_q,
            'unidad_medida': uom_kg,
            'proveedor': sup,
            'nivel_peligrosidad': 'MEDIO'
        }
    )
    
    tubo, _ = Pipe.objects.get_or_create(
        sku="PIPE-TEST-001",
        defaults={
            'nombre': "Tubo PVC Test",
            'categoria': cat_t,
            'unidad_medida': uom_m,
            'proveedor': sup,
            'material': 'PVC',
            'diametro_nominal': Decimal('1.00'),
            'unidad_diametro': 'PULGADAS',
            'presion_nominal': 'PN10',
            'tipo_union': 'SOLDABLE',
            'tipo_uso': 'POTABLE'
        }
    )

    # Limpiar stocks previos
    StockChemical.objects.all().delete()
    StockPipe.objects.all().delete()

    print("Setup de datos completado.")

    # --- ESCENARIO 1: ENTRADA ---
    print("\n1. Probando ENTRADA (Cloro -> Acueducto Norte)...")
    mov_e = MovimientoInventario.objects.create(
        producto=cloro,
        acueducto_destino=acu1,
        tipo_movimiento=MovimientoInventario.T_ENTRADA,
        cantidad=Decimal('100.000'),
        creado_por=admin_user,
        status=MovimientoInventario.STATUS_PENDIENTE
    )
    
    stock_e = StockChemical.objects.filter(producto=cloro, acueducto=acu1).first()
    qty_e = stock_e.cantidad if stock_e else 0
    print(f"Stock (Pendiente): {qty_e}")
    
    mov_e.status = MovimientoInventario.STATUS_APROBADO
    mov_e.save()
    
    stock_e = StockChemical.objects.get(producto=cloro, acueducto=acu1)
    print(f"Stock (Aprobado): {stock_e.cantidad}")
    assert stock_e.cantidad == Decimal('100.000')

    # --- ESCENARIO 2: SALIDA ---
    print("\n2. Probando SALIDA (Cloro -> Acueducto Norte)...")
    mov_s = MovimientoInventario.objects.create(
        producto=cloro,
        acueducto_origen=acu1,
        tipo_movimiento=MovimientoInventario.T_SALIDA,
        cantidad=Decimal('30.000'),
        creado_por=admin_user,
        status=MovimientoInventario.STATUS_PENDIENTE
    )
    
    mov_s.status = MovimientoInventario.STATUS_APROBADO
    mov_s.save()
    
    stock_s = StockChemical.objects.get(producto=cloro, acueducto=acu1)
    print(f"Stock despues de SALIDA: {stock_s.cantidad}")
    assert stock_s.cantidad == Decimal('70.000')

    # --- ESCENARIO 3: SALIDA FALLIDA (Stock Insuficiente) ---
    print("\n3. Probando SALIDA FALLIDA (Cantidad mayor al stock)...")
    mov_f = MovimientoInventario.objects.create(
        producto=cloro,
        acueducto_origen=acu1,
        tipo_movimiento=MovimientoInventario.T_SALIDA,
        cantidad=Decimal('200.000'),
        creado_por=admin_user,
        status=MovimientoInventario.STATUS_PENDIENTE
    )
    
    try:
        mov_f.status = MovimientoInventario.STATUS_APROBADO
        mov_f.save()
        print("ERROR: La validacion de stock insuficiente no funciono.")
    except ValidationError as e:
        print(f"EXITO: Validacion detectada correctamente: {e}")

    # --- ESCENARIO 4: TRANSFERENCIA ---
    print("\n4. Probando TRANSFERENCIA (Tubo -> De Norte a Sur)...")
    # Primero cargar stock en norte
    MovimientoInventario.objects.create(
        producto=tubo,
        acueducto_destino=acu1,
        tipo_movimiento=MovimientoInventario.T_ENTRADA,
        cantidad=Decimal('50.000'),
        creado_por=admin_user,
        status=MovimientoInventario.STATUS_APROBADO
    )
    
    print("Stock inicial en Norte: 50, en Sur: 0")
    mov_t = MovimientoInventario.objects.create(
        producto=tubo,
        acueducto_origen=acu1,
        acueducto_destino=acu2,
        tipo_movimiento=MovimientoInventario.T_TRANSFER,
        cantidad=Decimal('20.000'),
        creado_por=admin_user,
        status=MovimientoInventario.STATUS_PENDIENTE
    )
    
    mov_t.status = MovimientoInventario.STATUS_APROBADO
    mov_t.save()
    
    st_norte = StockPipe.objects.get(producto=tubo, acueducto=acu1)
    st_sur = StockPipe.objects.get(producto=tubo, acueducto=acu2)
    print(f"Stock en Norte: {st_norte.cantidad}, en Sur: {st_sur.cantidad}")
    assert st_norte.cantidad == Decimal('30.000')
    assert st_sur.cantidad == Decimal('20.000')

    # --- ESCENARIO 5: AJUSTE ---
    print("\n5. Probando AJUSTE (Tubo -> Incremento en Sur)...")
    mov_a = MovimientoInventario.objects.create(
        producto=tubo,
        acueducto_destino=acu2, # En ajuste, destino suma
        tipo_movimiento=MovimientoInventario.T_AJUSTE,
        cantidad=Decimal('5.000'),
        creado_por=admin_user,
        status=MovimientoInventario.STATUS_PENDIENTE
    )
    
    mov_a.status = MovimientoInventario.STATUS_APROBADO
    mov_a.save()
    
    st_ajuste = StockPipe.objects.get(producto=tubo, acueducto=acu2)
    print(f"Stock en Sur despues de ajuste: {st_ajuste.cantidad}")
    assert st_ajuste.cantidad == Decimal('25.000')

    print("\n--- TODAS LAS PRUEBAS EXHAUSTIVAS COMPLETADAS CON EXITO ---")

if __name__ == "__main__":
    run_exhaustive_tests()
