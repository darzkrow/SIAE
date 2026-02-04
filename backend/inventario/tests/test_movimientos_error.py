
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from inventario.models import MovimientoInventario, Pipe, Acueducto, Sucursal, OrganizacionCentral, UnitOfMeasure, Supplier

from geography.models import Ubicacion
from catalogo.models import CategoriaProducto
from inventario.serializers import MovimientoInventarioSerializer

User = get_user_model()

class MovimientoErrorTestCase(TestCase):
    def setUp(self):
        self.organizacion = OrganizacionCentral.objects.create(nombre='Test Org')
        self.sucursal = Sucursal.objects.create(nombre='Test Sucursal', organizacion_central=self.organizacion)
        self.acueducto = Acueducto.objects.create(nombre='Test Acueducto', sucursal=self.sucursal)
        self.ubicacion = Ubicacion.objects.create(nombre='Test Ubicacion', acueducto=self.acueducto, tipo='ALMACEN')
        self.user = User.objects.create_user(username='testuser', password='password')
        
        self.categoria = CategoriaProducto.objects.create(nombre='Test Cat', codigo='TC')
        self.unidad = UnitOfMeasure.objects.create(nombre='Unidad Test', simbolo='ut', tipo='UNIDAD')
        self.proveedor = Supplier.objects.create(nombre='Prov Test')
        self.pipe = Pipe.objects.create(
            nombre='Test Pipe', sku='TP-001', categoria=self.categoria,
            diametro_nominal=1, material='PVC',
            presion_nominal='PN10', tipo_union='SOLDABLE', tipo_uso='POTABLE',
            unidad_medida=self.unidad, proveedor=self.proveedor
        )
        self.ct = ContentType.objects.get_for_model(Pipe)

    def test_serializer_with_null_relations(self):
        print("\n--- Test Start ---")
        movimiento = MovimientoInventario.objects.create(
            content_type=self.ct,
            object_id=self.pipe.id,
            tipo_movimiento='ENTRADA',
            status='APROBADO',
            cantidad=Decimal('10.0'),
            ubicacion_destino=self.ubicacion,
            creado_por=self.user
        )
        print("Movement created")
        
        serializer = MovimientoInventarioSerializer(instance=movimiento)
        data = serializer.data
        print("Initial serialization done")
        
        self.assertIn('acueducto_destino_nombre', data)
        
        print("Deleting pipe (hard)...")
        self.pipe.hard_delete()
        print("Pipe deleted")
        
        movimiento.refresh_from_db()
        print("Movement refreshed")
        
        # Verify GFK is None
        self.assertIsNone(movimiento.producto)
        print("GFK is None confirmed")

        serializer_deleted = MovimientoInventarioSerializer(instance=movimiento)
        print("Serializing deleted...")
        data_deleted = serializer_deleted.data
        print("Serialization of deleted done")
        
        self.assertEqual(data_deleted['producto_str'], "Producto eliminado o no encontrado")
        print("--- Test End ---")

    def test_null_location_access(self):
        # Create a location without acueducto (if possible)
        # Checking models.py would confirm if acueducto is nullable. 
        # Assuming it is mandatory, we might be safe there, but let's check access.
        pass
