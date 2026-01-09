"""
Tests for inventario API views and endpoints.
Testing REST API functionality, permissions, and filters.
"""
import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto, Categoria,
    Tuberia, Equipo, StockTuberia, MovimientoInventario
)
from accounts.models import CustomUser

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationAPI(APITestCase):
    """Test authentication endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.org = OrganizacionCentral.objects.create(nombre="Test Org")
        self.sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=self.org)
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role=CustomUser.ROLE_ADMIN
        )
        
        self.operator_user = CustomUser.objects.create_user(
            username='operator',
            email='operator@test.com',
            password='oper123',
            role=CustomUser.ROLE_OPERADOR,
            sucursal=self.sucursal
        )
    
    def test_login_success(self):
        """Test successful login returns token."""
        url = '/api/accounts/login/'
        data = {'username': 'admin', 'password': 'admin123'}
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data or 'access' in response.data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials fails."""
        url = '/api/accounts/login/'
        data = {'username': 'admin', 'password': 'wrongpass'}
        response = self.client.post(url, data, format='json')
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]


@pytest.mark.django_db
class TestTuberiaAPI(APITestCase):
    """Test Tuberia CRUD endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        self.sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            role=CustomUser.ROLE_ADMIN
        )
        
        self.categoria = Categoria.objects.create(nombre="Tuberías PVC")
        
        self.tuberia = Tuberia.objects.create(
            nombre="Tubería PVC 110mm",
            categoria=self.categoria,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=110,
            longitud_m=6.0
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_tuberias(self):
        """Test listing tuberias."""
        url = '/api/tuberias/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_create_tuberia_as_admin(self):
        """Test that ADMIN can create tuberia."""
        url = '/api/tuberias/'
        data = {
            'nombre': 'Nueva Tubería',
            'categoria': self.categoria.id,
            'material': Tuberia.MATERIAL_PVC,
            'tipo_uso': Tuberia.USO_POTABLE,
            'diametro_nominal_mm': 100,
            'longitud_m': 6.0
        }
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Tuberia.objects.filter(nombre='Nueva Tubería').exists()


@pytest.mark.django_db
class TestStockAPI(APITestCase):
    """Test Stock API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        self.sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        self.acueducto = Acueducto.objects.create(nombre="Acueducto Test", sucursal=self.sucursal)
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            role=CustomUser.ROLE_ADMIN
        )
        
        categoria = Categoria.objects.create(nombre="Test Cat")
        self.tuberia = Tuberia.objects.create(
            nombre="Tubería Test",
            categoria=categoria,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=100,
            longitud_m=6.0
        )
        
        self.stock = StockTuberia.objects.create(
            tuberia=self.tuberia,
            acueducto=self.acueducto,
            cantidad=50
        )
        
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_stock(self):
        """Test listing stock."""
        url = '/api/stock-tuberias/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
class TestMovimientosAPI(APITestCase):
    """Test Movimientos API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        self.sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        self.acueducto = Acueducto.objects.create(nombre="Acueducto Test", sucursal=self.sucursal)
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            role=CustomUser.ROLE_ADMIN
        )
        
        categoria = Categoria.objects.create(nombre="Test Cat")
        self.tuberia = Tuberia.objects.create(
            nombre="Tubería Test",
            categoria=categoria,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=100,
            longitud_m=6.0
        )
        
        StockTuberia.objects.create(
            tuberia=self.tuberia,
            acueducto=self.acueducto,
            cantidad=100
        )
        
        self.client.force_authenticate(user=self.admin_user)
    
    def test_create_movimiento_entrada(self):
        """Test creating ENTRADA movement."""
        url = '/api/movimientos/'
        data = {
            'tuberia': self.tuberia.id,
            'tipo_movimiento': MovimientoInventario.T_ENTRADA,
            'acueducto_destino': self.acueducto.id,
            'cantidad': 20,
            'razon': 'Compra nueva'
        }
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify stock increased
        stock = StockTuberia.objects.get(tuberia=self.tuberia, acueducto=self.acueducto)
        assert stock.cantidad == 120


@pytest.mark.django_db
class TestReportesAPI(APITestCase):
    """Test Reportes API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            role=CustomUser.ROLE_ADMIN
        )
        
        self.client.force_authenticate(user=self.admin_user)
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint."""
        url = '/api/reportes/dashboard_stats/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_tuberias' in response.data
        assert 'total_equipos' in response.data
    
    def test_stock_por_sucursal(self):
        """Test stock by sucursal endpoint."""
        url = '/api/reportes/stock_por_sucursal/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)


@pytest.mark.django_db
class TestPermissionsAPI(APITestCase):
    """Test API permissions for different user roles."""
    
    def setUp(self):
        self.client = APIClient()
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        self.sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        
        self.operator_user = CustomUser.objects.create_user(
            username='operator',
            password='oper123',
            role=CustomUser.ROLE_OPERADOR,
            sucursal=self.sucursal
        )
        
        self.categoria = Categoria.objects.create(nombre="Test Cat")
    
    def test_operator_cannot_create_tuberia(self):
        """Test that OPERADOR cannot create tuberias."""
        self.client.force_authenticate(user=self.operator_user)
        
        url = '/api/tuberias/'
        data = {
            'nombre': 'Nueva Tubería',
            'categoria': self.categoria.id,
            'material': Tuberia.MATERIAL_PVC,
            'tipo_uso': Tuberia.USO_POTABLE,
            'diametro_nominal_mm': 100,
            'longitud_m': 6.0
        }
        response = self.client.post(url, data, format='json')
        
        # Should be forbidden (403) or method not allowed (405)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED]
    
    def test_unauthenticated_cannot_access_api(self):
        """Test that unauthenticated users cannot access API."""
        # Don't authenticate
        url = '/api/tuberias/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
