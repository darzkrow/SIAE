from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from inventario.models import (
    StockChemical, MovimientoInventario, UnitOfMeasure
)
from geography.models import Location as Ubicacion, State, Municipality, Parish
from catalogo.models import CategoriaProducto, Marca
from institucion.models import Acueducto, Sucursal, OrganizacionCentral
from inventario.models import ChemicalProduct

User = get_user_model()

class InventarioTests(TransactionTestCase):
    def setUp(self):
        # Setup básico organizacional
        self.org = OrganizacionCentral.objects.create(nombre='Test Org', rif='J-1')
        self.suc = Sucursal.objects.create(nombre='Test Suc', organizacion_central=self.org)
        self.acu = Acueducto.objects.create(nombre='Test Acu', sucursal=self.suc)
        
        # Setup geográfico
        self.state = State.objects.create(name='Test State')
        self.mun = Municipality.objects.create(name='Test Mun', state=self.state)
        self.par = Parish.objects.create(name='Test Par', municipality=self.mun)
        self.ubi = Ubicacion.objects.create(
            acueducto=self.acu,
            parish=self.par,
            nombre='Almacén Central',
            tipo='ALMACEN'
        )
        
        # Setup producto
        self.cat = CategoriaProducto.objects.create(nombre='Químicos', codigo='QUI')
        self.udm = UnitOfMeasure.objects.create(nombre='Kilo', simbolo='kg', tipo='PESO')
        self.prov = Supplier.objects.create(nombre='Proveedor Test', rif='J-123')
        self.prod = ChemicalProduct.objects.create(
            nombre='Cloro',
            sku='QUI-001',
            categoria=self.cat,
            unidad_medida=self.udm,
            proveedor=self.prov
        )
        
        # Setup usuario
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_tc_inv_01_entrada_stock(self):
        """TC-INV-01: Verificar entrada de stock y actualización de cantidades"""
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(self.prod)
        
        try:
            mov = MovimientoInventario.objects.create(
                tipo_movimiento=MovimientoInventario.T_ENTRADA,
                content_type=ct,
                object_id=self.prod.id,
                cantidad=Decimal('100.00'),
                ubicacion_destino=self.ubi,
                status=MovimientoInventario.STATUS_APROBADO,
                creado_por=self.user
            )
        except Exception as e:
            if hasattr(e, 'message_dict'):
                print(f"VALIDATION ERROR DETAILS: {e.message_dict}")
            raise e
        
        stock = StockChemical.objects.get(producto=self.prod, ubicacion=self.ubi)
        self.assertEqual(stock.cantidad, Decimal('100.00'))

    def test_tc_inv_03_error_salida_insuficiente(self):
        """TC-INV-03: Salida sin stock debe fallar"""
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(self.prod)
        from django.core.exceptions import ValidationError
        
        # Primero necesitamos algo de stock para que intente restar
        StockChemical.objects.create(producto=self.prod, ubicacion=self.ubi, cantidad=Decimal('10.00'))

        with self.assertRaises(ValidationError):
            MovimientoInventario.objects.create(
                tipo_movimiento=MovimientoInventario.T_SALIDA,
                content_type=ct,
                object_id=self.prod.id,
                cantidad=Decimal('500.00'),
                ubicacion_origen=self.ubi,
                status=MovimientoInventario.STATUS_APROBADO,
                creado_por=self.user
            )
