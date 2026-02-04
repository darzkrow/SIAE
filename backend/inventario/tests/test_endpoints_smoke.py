
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from institucion.models import OrganizacionCentral, Sucursal, Acueducto
from catalogo.models import CategoriaProducto
from django.test import override_settings

User = get_user_model()

from django.test import override_settings

@override_settings(DEBUG_PROPAGATE_EXCEPTIONS=True)
class EndpointSmokeTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Setup basic data
        self.organizacion = OrganizacionCentral.objects.create(nombre='Smoke Org')
        self.sucursal = Sucursal.objects.create(nombre='Smoke Branch', organizacion_central=self.organizacion)
        self.acueducto = Acueducto.objects.create(nombre='Smoke Acueducto', sucursal=self.sucursal)
        self.categoria = CategoriaProducto.objects.create(nombre='Smoke Cat', codigo='SCT')
        self.categoria_bom = CategoriaProducto.objects.create(nombre='Bombas y Motores', codigo='BOM')

        # Setup User
        self.user = User.objects.create_user(
            username='api_tester',
            password='password123',
            role='ADMIN',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_health_check(self):
        # Health check might not be DRF, better use standard client or just skip format
        response = self.client.get('/health/') 
        self.assertEqual(response.status_code, 200)

    def test_catalog_endpoints(self):
        endpoints = [
            '/api/catalog/categorias/',
        ]
        for ep in endpoints:
            response = self.client.get(ep, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed: {ep}")

    def test_inventory_endpoints(self):
        endpoints = [
            '/api/chemicals/',
            '/api/pipes/',
            '/api/pumps/',
            '/api/accessories/',
        ]
        for ep in endpoints:
            response = self.client.get(ep, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed: {ep}")

    def test_stock_endpoints(self):
        endpoints = [
            '/api/stock-chemicals/',
            '/api/stock-pipes/',
            '/api/stock-pumps/',
            '/api/stock-accessories/',
        ]
        for ep in endpoints:
            response = self.client.get(ep, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed: {ep}")

    def test_movimientos_endpoint(self):
        response = self.client.get('/api/movimientos/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reportes_endpoints(self):
        endpoints = [
            '/api/reportes-v2/dashboard_stats/',
            '/api/reportes-v2/movimientos_recientes/',
            '/api/reportes-v2/stock_por_sucursal/',
            '/api/reportes-v2/resumen_movimientos/',
        ]
        for ep in endpoints:
            response = self.client.get(ep, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed: {ep}")

    def test_geography_endpoints(self):
        endpoints = [
            '/api/geography/states/',
            '/api/geography/municipalities/',
            '/api/geography/parishes/',
            '/api/geography/ubicaciones/',
        ]
        for ep in endpoints:
            response = self.client.get(ep, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed: {ep}")
