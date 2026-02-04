"""
Basic API compatibility tests for Hidroven Organizational Restructuring.
Tests the fundamental API endpoints without complex imports.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import OrganizacionCentral, Sucursal, Acueducto

User = get_user_model()


class BasicAPICompatibilityTest(APITestCase):
    """Basic test for API compatibility without complex imports."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create basic test data
        self.org_central = OrganizacionCentral.objects.create(
            nombre='HIDROVEN',
            rif='G-20000001-0'
        )
        
        self.sucursal = Sucursal.objects.create(
            nombre='Sucursal Zulia',
            organizacion_central=self.org_central,
            codigo='ZUL'
        )
        
        self.acueducto = Acueducto.objects.create(
            nombre='Acueducto Maracaibo',
            sucursal=self.sucursal,
            codigo='ACU-ZUL-001'
        )
    
    def test_models_exist(self):
        """Test that the basic models exist and work."""
        self.assertEqual(OrganizacionCentral.objects.count(), 1)
        self.assertEqual(Sucursal.objects.count(), 1)
        self.assertEqual(Acueducto.objects.count(), 1)
        
        # Test relationships
        self.assertEqual(self.org_central.sucursales.count(), 1)
        self.assertEqual(self.sucursal.acueductos.count(), 1)
        
        # Test string representations
        self.assertEqual(str(self.org_central), 'HIDROVEN')
        self.assertEqual(str(self.sucursal), 'Sucursal Zulia (HIDROVEN)')
        self.assertEqual(str(self.acueducto), 'Acueducto Maracaibo - Sucursal Zulia')
    
    def test_legacy_api_endpoints_exist(self):
        """Test that legacy API endpoints can be accessed."""
        # Test that the URLs exist in the inventario app (where they're currently defined)
        try:
            response = self.client.get('/api/organizaciones/')
            # Should return 200 OK or at least not 404
            self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # If there's an import error, that's what we're trying to fix
            self.fail(f"Legacy API endpoint failed: {str(e)}")
    
    def test_data_format_compatibility(self):
        """Test that data formats are compatible."""
        # Test OrganizacionCentral data format
        org_data = {
            'id': self.org_central.id,
            'nombre': self.org_central.nombre,
            'rif': self.org_central.rif,
            'parent': self.org_central.parent_id,
        }
        
        # Verify expected fields exist
        self.assertIsInstance(org_data['id'], int)
        self.assertIsInstance(org_data['nombre'], str)
        self.assertEqual(org_data['nombre'], 'HIDROVEN')
        
        # Test Sucursal data format
        sucursal_data = {
            'id': self.sucursal.id,
            'nombre': self.sucursal.nombre,
            'organizacion_central': self.sucursal.organizacion_central.id,
            'codigo': self.sucursal.codigo,
        }
        
        self.assertIsInstance(sucursal_data['id'], int)
        self.assertIsInstance(sucursal_data['organizacion_central'], int)
        self.assertEqual(sucursal_data['codigo'], 'ZUL')
    
    def test_backward_compatibility_requirements(self):
        """Test that backward compatibility requirements are met."""
        # Requirement 9.1: Maintain backward compatibility with existing endpoints
        # This test verifies that the data structures remain compatible
        
        # Test that existing model fields are preserved
        org_fields = ['nombre', 'rif', 'parent']
        for field in org_fields:
            self.assertTrue(hasattr(OrganizacionCentral, field))
        
        sucursal_fields = ['nombre', 'organizacion_central', 'codigo', 'direccion', 'telefono']
        for field in sucursal_fields:
            self.assertTrue(hasattr(Sucursal, field))
        
        acueducto_fields = ['nombre', 'sucursal', 'codigo', 'ubicacion']
        for field in acueducto_fields:
            self.assertTrue(hasattr(Acueducto, field))
    
    def test_new_hierarchical_models_exist(self):
        """Test that new hierarchical models exist."""
        from .models import Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional
        
        # Test that models can be imported and have expected fields
        self.assertTrue(hasattr(Empresa, 'nombre'))
        self.assertTrue(hasattr(Empresa, 'codigo'))
        self.assertTrue(hasattr(Empresa, 'rif'))
        
        self.assertTrue(hasattr(Vicepresidencia, 'empresa'))
        self.assertTrue(hasattr(Vicepresidencia, 'tipo'))
        
        self.assertTrue(hasattr(UnidadOrganizacional, 'vicepresidencia'))
        self.assertTrue(hasattr(UnidadOrganizacional, 'tipo'))
        
        self.assertTrue(hasattr(AlmacenRegional, 'prefijo'))
        self.assertTrue(hasattr(AlmacenRegional, 'unidad_organizacional'))
    
    def test_migration_support_models_exist(self):
        """Test that migration support models exist."""
        from .models import MigracionOrganizacional
        
        # Test that migration model exists and has expected fields
        self.assertTrue(hasattr(MigracionOrganizacional, 'organizacion_central_id'))
        self.assertTrue(hasattr(MigracionOrganizacional, 'sucursal_id'))
        self.assertTrue(hasattr(MigracionOrganizacional, 'acueducto_id'))
        self.assertTrue(hasattr(MigracionOrganizacional, 'empresa'))
        self.assertTrue(hasattr(MigracionOrganizacional, 'estado_migracion'))
    
    def test_asset_tracking_models_exist(self):
        """Test that asset tracking models exist."""
        from .models import ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado
        
        # Test that asset models exist and have expected fields
        self.assertTrue(hasattr(ActivoInventario, 'codigo_actual'))
        self.assertTrue(hasattr(ActivoInventario, 'almacen_actual'))
        self.assertTrue(hasattr(ActivoInventario, 'estado'))
        
        self.assertTrue(hasattr(HistorialMovimientoActivo, 'activo'))
        self.assertTrue(hasattr(HistorialMovimientoActivo, 'tipo_movimiento'))
        
        self.assertTrue(hasattr(SolicitudTraslado, 'activo'))
        self.assertTrue(hasattr(SolicitudTraslado, 'almacen_origen'))
        self.assertTrue(hasattr(SolicitudTraslado, 'almacen_destino'))
    
    def test_dual_api_support_concept(self):
        """Test the concept of dual API support."""
        # This test verifies that both old and new models can coexist
        
        # Create new hierarchical structure
        from .models import Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional
        
        empresa = Empresa.objects.create(
            nombre='HIDROVEN S.A.',
            codigo='HIDROVEN',
            rif='G-20000001-0'
        )
        
        vp = Vicepresidencia.objects.create(
            empresa=empresa,
            nombre='VP Operaciones',
            codigo='VP-OP',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        unidad = UnidadOrganizacional.objects.create(
            vicepresidencia=vp,
            nombre='Gerencia Almacenes',
            codigo='GER-ALM',
            tipo='GERENCIA'
        )
        
        almacen = AlmacenRegional.objects.create(
            unidad_organizacional=unidad,
            nombre='Almacén Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo'
        )
        
        # Verify both structures exist simultaneously
        self.assertEqual(OrganizacionCentral.objects.count(), 1)  # Legacy
        self.assertEqual(Empresa.objects.count(), 1)  # New
        
        # Verify they can reference similar data
        self.assertEqual(self.org_central.nombre, 'HIDROVEN')
        self.assertEqual(empresa.nombre, 'HIDROVEN S.A.')
        self.assertEqual(self.org_central.rif, empresa.rif)
        
        # Verify warehouse prefixes match
        self.assertEqual(self.sucursal.codigo, almacen.prefijo)


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'rest_framework',
                'mptt',
                'institucion',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])