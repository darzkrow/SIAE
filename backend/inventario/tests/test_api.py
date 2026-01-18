"""
Tests básicos para el sistema de inventario.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from institucion.models import OrganizacionCentral, Sucursal, Acueducto
from inventario.models import Category, UnitOfMeasure, Supplier
from geography.models import State, Municipality, Parish, Ubicacion

User = get_user_model()


class BaseTestCase(TestCase):
    """Clase base con configuración común para todos los tests."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Crear organización y sucursal
        self.org = OrganizacionCentral.objects.create(
            nombre="HIDROVEN",
            rif="J-12345678-9"
        )
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Central",
            organizacion_central=self.org,
            codigo="SC001"
        )
        
        # Crear acueducto
        self.acueducto = Acueducto.objects.create(
            nombre="Acueducto Principal",
            sucursal=self.sucursal,
            codigo="AP001"
        )
        
        # Crear geografía
        self.state = State.objects.create(name="Distrito Capital")
        self.municipality = Municipality.objects.create(
            name="Libertador",
            state=self.state
        )
        self.parish = Parish.objects.create(
            name="Catedral",
            municipality=self.municipality
        )
        
        # Crear ubicación
        self.ubicacion = Ubicacion.objects.create(
            nombre="Almacén Principal",
            tipo=Ubicacion.TipoUbicacion.ALMACEN,
            parish=self.parish,
            acueducto=self.acueducto
        )
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='ADMIN',
            sucursal=self.sucursal
        )
        
        self.operator_user = User.objects.create_user(
            username='operator',
            email='operator@test.com',
            password='operator123',
            role='OPERADOR',
            sucursal=self.sucursal
        )
        
        # Cliente API
        self.client = APIClient()


class AuthenticationTests(BaseTestCase):
    """Tests de autenticación."""
    
    def test_login_success(self):
        """Test de login exitoso."""
        response = self.client.post('/api/accounts/api-token-auth/', {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_login_invalid_credentials(self):
        """Test de login con credenciales inválidas."""
        response = self.client.post('/api/accounts/api-token-auth/', {
            'username': 'admin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_protected_endpoint_without_auth(self):
        """Test de acceso a endpoint protegido sin autenticación."""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_with_auth(self):
        """Test de acceso a endpoint protegido con autenticación."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CategoryTests(BaseTestCase):
    """Tests para el modelo Category."""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin_user)
        self.category = Category.objects.create(
            nombre="Tuberías",
            codigo="TUB",
            activo=True,
            orden=1
        )
    
    def test_list_categories(self):
        """Test de listado de categorías."""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_category(self):
        """Test de creación de categoría."""
        data = {
            'nombre': 'Accesorios',
            'codigo': 'ACC',
            'activo': True,
            'orden': 2
        }
        response = self.client.post('/api/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
    
    def test_update_category(self):
        """Test de actualización de categoría."""
        data = {'nombre': 'Tuberías PVC'}
        response = self.client.patch(f'/api/categories/{self.category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.nombre, 'Tuberías PVC')
    
    def test_delete_category(self):
        """Test de eliminación de categoría."""
        response = self.client.delete(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)


class PermissionsTests(BaseTestCase):
    """Tests de permisos."""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(
            nombre="Test Category",
            codigo="TST",
            activo=True,
            orden=1
        )
    
    def test_operator_can_read(self):
        """Test de que operador puede leer."""
        self.client.force_authenticate(user=self.operator_user)
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_operator_cannot_create(self):
        """Test de que operador no puede crear."""
        self.client.force_authenticate(user=self.operator_user)
        data = {
            'nombre': 'New Category',
            'codigo': 'NEW',
            'activo': True,
            'orden': 2
        }
        response = self.client.post('/api/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_create(self):
        """Test de que admin puede crear."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'nombre': 'New Category',
            'codigo': 'NEW',
            'activo': True,
            'orden': 2
        }
        response = self.client.post('/api/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GeographyTests(BaseTestCase):
    """Tests para modelos geográficos."""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_states(self):
        """Test de listado de estados."""
        response = self.client.get('/api/geography/states/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_municipalities(self):
        """Test de listado de municipios."""
        response = self.client.get('/api/geography/municipalities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_parishes(self):
        """Test de listado de parroquias."""
        response = self.client.get('/api/geography/parishes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_ubicacion(self):
        """Test de creación de ubicación."""
        data = {
            'nombre': 'Almacén Secundario',
            'tipo': 'ALMACEN',
            'parish': self.parish.id,
            'acueducto': self.acueducto.id,
            'activa': True
        }
        response = self.client.post('/api/geography/ubicaciones/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UnitOfMeasureTests(BaseTestCase):
    """Tests para unidades de medida."""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin_user)
    
    def test_create_unit(self):
        """Test de creación de unidad de medida."""
        data = {
            'nombre': 'Metros',
            'simbolo': 'm',
            'tipo': 'LONGITUD',
            'activo': True
        }
        response = self.client.post('/api/units/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_units(self):
        """Test de listado de unidades."""
        UnitOfMeasure.objects.create(
            nombre='Kilogramos',
            simbolo='kg',
            tipo='PESO',
            activo=True
        )
        response = self.client.get('/api/units/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SupplierTests(BaseTestCase):
    """Tests para proveedores."""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin_user)
    
    def test_create_supplier(self):
        """Test de creación de proveedor."""
        data = {
            'nombre': 'Proveedor Test',
            'rif': 'J-98765432-1',
            'codigo': 'PROV001',
            'activo': True
        }
        response = self.client.post('/api/suppliers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_suppliers(self):
        """Test de listado de proveedores."""
        Supplier.objects.create(
            nombre='Proveedor 1',
            rif='J-11111111-1',
            codigo='P001',
            activo=True
        )
        response = self.client.get('/api/suppliers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
