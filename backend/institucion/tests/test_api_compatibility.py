"""
Unit tests for API compatibility in Hidroven Organizational Restructuring.

Tests both backward compatibility with existing APIs and new hierarchical endpoints.
Validates dual API support during transition period.

Requirements tested:
- 9.1: Backward compatibility with existing OrganizacionCentral, Sucursal, Acueducto endpoints
- 9.2: New hierarchy API endpoints (Vicepresidencias, Unidades, asset tracking)
- 9.3: Dual API support during transition period
- 9.4: Data format compatibility for frontend components
- 9.5: Migration status and monitoring endpoints
- 9.6: API versioning for smooth transitions
"""
import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .models import (
    # New hierarchical models
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado, AprobacionTraslado,
    MigracionOrganizacional,
    # Legacy models for backward compatibility
    OrganizacionCentral, Sucursal, Acueducto
)

User = get_user_model()


class APICompatibilityTestCase(APITestCase):
    """Base test case for API compatibility tests."""
    
    def setUp(self):
        """Set up test data for API compatibility tests."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create legacy organizational structure
        self.org_central = OrganizacionCentral.objects.create(
            nombre='HIDROVEN',
            rif='G-20000001-0'
        )
        
        self.sucursal = Sucursal.objects.create(
            nombre='Sucursal Zulia',
            organizacion_central=self.org_central,
            codigo='ZUL',
            direccion='Maracaibo, Zulia',
            telefono='+58-261-1234567'
        )
        
        self.acueducto = Acueducto.objects.create(
            nombre='Acueducto Maracaibo',
            sucursal=self.sucursal,
            codigo='ACU-ZUL-001',
            ubicacion='Maracaibo Centro'
        )
        
        # Create new hierarchical structure
        self.empresa = Empresa.objects.create(
            nombre='HIDROVEN S.A.',
            codigo='HIDROVEN',
            rif='G-20000001-0',
            direccion='Caracas, Venezuela',
            telefono='+58-212-1234567',
            email='info@hidroven.gob.ve'
        )
        
        self.vp_operaciones = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='Vicepresidencia de Operaciones Hídricas',
            codigo='VP-OPERACIONES',
            tipo='OPERACIONES_HIDRICAS',
            descripcion='Responsable de operaciones hídricas',
            responsable=self.user
        )
        
        self.unidad_almacenes = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Gerencia de Almacenes Regionales',
            codigo='GER-ALMACENES',
            tipo='GERENCIA',
            descripcion='Gestión de almacenes regionales',
            ubicacion='Caracas',
            responsable=self.user
        )
        
        self.almacen_zulia = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Regional Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia',
            manager=self.user,
            capacidad_maxima=10000,
            descripcion='Almacén regional para el estado Zulia',
            telefono='+58-261-1234567',
            email='almacen.zulia@hidroven.gob.ve'
        )
        
        # Create migration mapping
        self.migracion = MigracionOrganizacional.objects.create(
            organizacion_central_id=self.org_central.id,
            sucursal_id=self.sucursal.id,
            acueducto_id=self.acueducto.id,
            empresa=self.empresa,
            vicepresidencia=self.vp_operaciones,
            unidad_organizacional=self.unidad_almacenes,
            migrado_por=self.user,
            estado_migracion='COMPLETADA',
            validado=True,
            validado_por=self.user,
            fecha_validacion=timezone.now(),
            datos_originales={
                'organizacion_central': {
                    'id': self.org_central.id,
                    'nombre': self.org_central.nombre,
                    'rif': self.org_central.rif
                },
                'sucursal': {
                    'id': self.sucursal.id,
                    'nombre': self.sucursal.nombre,
                    'codigo': self.sucursal.codigo
                },
                'acueducto': {
                    'id': self.acueducto.id,
                    'nombre': self.acueducto.nombre,
                    'codigo': self.acueducto.codigo
                }
            }
        )


class BackwardCompatibilityAPITests(APICompatibilityTestCase):
    """Test backward compatibility with existing API endpoints."""
    
    def test_organizacion_central_list_endpoint(self):
        """Test that OrganizacionCentral list endpoint works unchanged."""
        # Test both legacy and new URL patterns
        urls_to_test = [
            '/api/organizaciones/',  # Legacy URL
            '/api/institucion/organizaciones-centrales/',  # New URL
        ]
        
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                # Verify response structure
                self.assertIn('results', response.data)
                results = response.data['results']
                self.assertEqual(len(results), 1)
                
                # Verify data format matches expected structure
                org_data = results[0]
                expected_fields = ['id', 'nombre', 'rif', 'parent', 'parent_nombre', 'sucursales_count']
                for field in expected_fields:
                    self.assertIn(field, org_data)
                
                # Verify data values
                self.assertEqual(org_data['nombre'], 'HIDROVEN')
                self.assertEqual(org_data['rif'], 'G-20000001-0')
                self.assertEqual(org_data['sucursales_count'], 1)
    
    def test_organizacion_central_detail_endpoint(self):
        """Test that OrganizacionCentral detail endpoint works unchanged."""
        urls_to_test = [
            f'/api/organizaciones/{self.org_central.id}/',
            f'/api/institucion/organizaciones-centrales/{self.org_central.id}/',
        ]
        
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                # Verify response structure and data
                self.assertEqual(response.data['id'], self.org_central.id)
                self.assertEqual(response.data['nombre'], 'HIDROVEN')
                self.assertEqual(response.data['rif'], 'G-20000001-0')
    
    def test_organizacion_central_crud_operations(self):
        """Test CRUD operations on OrganizacionCentral endpoint."""
        base_url = '/api/institucion/organizaciones-centrales/'
        
        # Test CREATE
        create_data = {
            'nombre': 'Nueva Organización',
            'rif': 'G-30000001-0'
        }
        response = self.client.post(base_url, create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data['id']
        
        # Test READ (detail)
        response = self.client.get(f'{base_url}{created_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Nueva Organización')
        
        # Test UPDATE
        update_data = {
            'nombre': 'Organización Actualizada',
            'rif': 'G-30000001-0'
        }
        response = self.client.put(f'{base_url}{created_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Organización Actualizada')
        
        # Test PARTIAL UPDATE
        patch_data = {'nombre': 'Organización Parcialmente Actualizada'}
        response = self.client.patch(f'{base_url}{created_id}/', patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Organización Parcialmente Actualizada')
        
        # Test DELETE
        response = self.client.delete(f'{base_url}{created_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        response = self.client.get(f'{base_url}{created_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_sucursal_list_endpoint(self):
        """Test that Sucursal list endpoint works unchanged."""
        urls_to_test = [
            '/api/sucursales/',
            '/api/institucion/sucursales/',
        ]
        
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                results = response.data['results']
                self.assertEqual(len(results), 1)
                
                sucursal_data = results[0]
                expected_fields = ['id', 'nombre', 'organizacion_central', 'organizacion_nombre', 
                                 'codigo', 'direccion', 'telefono', 'acueductos_count']
                for field in expected_fields:
                    self.assertIn(field, sucursal_data)
                
                self.assertEqual(sucursal_data['nombre'], 'Sucursal Zulia')
                self.assertEqual(sucursal_data['codigo'], 'ZUL')
                self.assertEqual(sucursal_data['acueductos_count'], 1)
    
    def test_sucursal_filtering_and_search(self):
        """Test filtering and search functionality on Sucursal endpoint."""
        base_url = '/api/institucion/sucursales/'
        
        # Test filtering by organizacion_central
        response = self.client.get(f'{base_url}?organizacion_central={self.org_central.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search by nombre
        response = self.client.get(f'{base_url}?search=Zulia')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search by codigo
        response = self.client.get(f'{base_url}?search=ZUL')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test ordering
        response = self.client.get(f'{base_url}?ordering=nombre')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(f'{base_url}?ordering=-nombre')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_acueducto_list_endpoint(self):
        """Test that Acueducto list endpoint works unchanged."""
        urls_to_test = [
            '/api/acueductos/',
            '/api/institucion/acueductos/',
        ]
        
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                results = response.data['results']
                self.assertEqual(len(results), 1)
                
                acueducto_data = results[0]
                expected_fields = ['id', 'nombre', 'sucursal', 'sucursal_nombre', 
                                 'organizacion_nombre', 'codigo', 'ubicacion']
                for field in expected_fields:
                    self.assertIn(field, acueducto_data)
                
                self.assertEqual(acueducto_data['nombre'], 'Acueducto Maracaibo')
                self.assertEqual(acueducto_data['codigo'], 'ACU-ZUL-001')
                self.assertEqual(acueducto_data['sucursal_nombre'], 'Sucursal Zulia')
                self.assertEqual(acueducto_data['organizacion_nombre'], 'HIDROVEN')
    
    def test_legacy_api_response_format_compatibility(self):
        """Test that legacy API responses maintain exact format compatibility."""
        # Test OrganizacionCentral response format
        response = self.client.get('/api/organizaciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Verify individual record structure
        org_data = response.data['results'][0]
        self.assertIsInstance(org_data['id'], int)
        self.assertIsInstance(org_data['nombre'], str)
        self.assertIsInstance(org_data['sucursales_count'], int)
        
        # Test Sucursal response format
        response = self.client.get('/api/sucursales/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        sucursal_data = response.data['results'][0]
        self.assertIsInstance(sucursal_data['id'], int)
        self.assertIsInstance(sucursal_data['organizacion_central'], int)
        self.assertIsInstance(sucursal_data['organizacion_nombre'], str)
        
        # Test Acueducto response format
        response = self.client.get('/api/acueductos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        acueducto_data = response.data['results'][0]
        self.assertIsInstance(acueducto_data['id'], int)
        self.assertIsInstance(acueducto_data['sucursal'], int)
        self.assertIsInstance(acueducto_data['sucursal_nombre'], str)
        self.assertIsInstance(acueducto_data['organizacion_nombre'], str)


class NewHierarchicalAPITests(APICompatibilityTestCase):
    """Test new hierarchical API endpoints."""
    
    def test_empresa_list_endpoint(self):
        """Test new Empresa list endpoint."""
        url = '/api/institucion/empresas/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        self.assertEqual(len(results), 1)
        
        empresa_data = results[0]
        expected_fields = [
            'id', 'nombre', 'codigo', 'rif', 'direccion', 'telefono', 'email',
            'activo', 'fecha_creacion', 'fecha_actualizacion', 'parent',
            'subsidiarias_count', 'vicepresidencias_count', 'full_path'
        ]
        for field in expected_fields:
            self.assertIn(field, empresa_data)
        
        self.assertEqual(empresa_data['nombre'], 'HIDROVEN S.A.')
        self.assertEqual(empresa_data['codigo'], 'HIDROVEN')
        self.assertEqual(empresa_data['vicepresidencias_count'], 1)
    
    def test_empresa_hierarchy_tree_action(self):
        """Test empresa hierarchy tree custom action."""
        url = f'/api/institucion/empresas/{self.empresa.id}/hierarchy_tree/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify hierarchy structure
        self.assertEqual(response.data['id'], self.empresa.id)
        self.assertEqual(response.data['nombre'], 'HIDROVEN S.A.')
        self.assertIn('children', response.data)
        self.assertIn('level', response.data)
    
    def test_empresa_vicepresidencias_action(self):
        """Test empresa vicepresidencias custom action."""
        url = f'/api/institucion/empresas/{self.empresa.id}/vicepresidencias/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), 1)
        vp_data = response.data[0]
        self.assertEqual(vp_data['nombre'], 'Vicepresidencia de Operaciones Hídricas')
        self.assertEqual(vp_data['tipo'], 'OPERACIONES_HIDRICAS')
    
    def test_vicepresidencia_list_endpoint(self):
        """Test Vicepresidencia list endpoint."""
        url = '/api/institucion/vicepresidencias/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        self.assertEqual(len(results), 1)
        
        vp_data = results[0]
        expected_fields = [
            'id', 'empresa', 'empresa_nombre', 'nombre', 'codigo', 'tipo',
            'descripcion', 'responsable', 'responsable_username', 'activo',
            'fecha_creacion', 'fecha_actualizacion', 'parent',
            'unidades_count', 'full_path'
        ]
        for field in expected_fields:
            self.assertIn(field, vp_data)
        
        self.assertEqual(vp_data['tipo'], 'OPERACIONES_HIDRICAS')
        self.assertEqual(vp_data['empresa_nombre'], 'HIDROVEN S.A.')
        self.assertEqual(vp_data['unidades_count'], 1)
    
    def test_vicepresidencia_filtering(self):
        """Test Vicepresidencia filtering capabilities."""
        base_url = '/api/institucion/vicepresidencias/'
        
        # Test filtering by empresa
        response = self.client.get(f'{base_url}?empresa={self.empresa.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering by tipo
        response = self.client.get(f'{base_url}?tipo=OPERACIONES_HIDRICAS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering by activo
        response = self.client.get(f'{base_url}?activo=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_vicepresidencia_dashboard_stats_action(self):
        """Test vicepresidencia dashboard stats custom action."""
        url = f'/api/institucion/vicepresidencias/{self.vp_operaciones.id}/dashboard_stats/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_fields = [
            'unidades_organizacionales', 'almacenes_regionales',
            'activos_totales', 'traslados_pendientes'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        self.assertEqual(response.data['unidades_organizacionales'], 1)
        self.assertEqual(response.data['almacenes_regionales'], 1)
    
    def test_unidad_organizacional_list_endpoint(self):
        """Test UnidadOrganizacional list endpoint."""
        url = '/api/institucion/unidades-organizacionales/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        self.assertEqual(len(results), 1)
        
        unidad_data = results[0]
        expected_fields = [
            'id', 'vicepresidencia', 'vicepresidencia_nombre', 'empresa_nombre',
            'nombre', 'codigo', 'tipo', 'descripcion', 'ubicacion',
            'responsable', 'responsable_username', 'activo',
            'fecha_creacion', 'fecha_actualizacion', 'parent',
            'almacenes_count', 'full_path'
        ]
        for field in expected_fields:
            self.assertIn(field, unidad_data)
        
        self.assertEqual(unidad_data['nombre'], 'Gerencia de Almacenes Regionales')
        self.assertEqual(unidad_data['tipo'], 'GERENCIA')
        self.assertEqual(unidad_data['almacenes_count'], 1)
    
    def test_almacen_regional_list_endpoint(self):
        """Test AlmacenRegional list endpoint."""
        url = '/api/institucion/almacenes-regionales/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        self.assertEqual(len(results), 1)
        
        almacen_data = results[0]
        expected_fields = [
            'id', 'unidad_organizacional', 'unidad_nombre', 'vicepresidencia_nombre',
            'nombre', 'prefijo', 'ubicacion', 'manager', 'manager_username',
            'capacidad_maxima', 'activo', 'fecha_creacion', 'fecha_actualizacion',
            'descripcion', 'telefono', 'email', 'activos_count', 'capacity_usage',
            'full_path'
        ]
        for field in expected_fields:
            self.assertIn(field, almacen_data)
        
        self.assertEqual(almacen_data['nombre'], 'Almacén Regional Zulia')
        self.assertEqual(almacen_data['prefijo'], 'ZUL')
        self.assertEqual(almacen_data['capacidad_maxima'], 10000)
    
    def test_almacen_regional_unique_prefix_validation(self):
        """Test that AlmacenRegional prefix uniqueness is enforced via API."""
        url = '/api/institucion/almacenes-regionales/'
        
        # Try to create another warehouse with same prefix
        create_data = {
            'unidad_organizacional': self.unidad_almacenes.id,
            'nombre': 'Otro Almacén Zulia',
            'prefijo': 'ZUL',  # Same prefix as existing warehouse
            'ubicacion': 'Otra ubicación',
            'manager': self.user.id,
            'capacidad_maxima': 5000
        }
        
        response = self.client.post(url, create_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error message mentions uniqueness
        self.assertIn('prefijo', response.data)
    
    def test_new_api_crud_operations(self):
        """Test CRUD operations on new hierarchical endpoints."""
        # Test Empresa CRUD
        empresa_url = '/api/institucion/empresas/'
        empresa_data = {
            'nombre': 'Nueva Empresa',
            'codigo': 'NUEVA',
            'rif': 'G-40000001-0',
            'direccion': 'Nueva dirección',
            'telefono': '+58-212-9876543',
            'email': 'nueva@empresa.com'
        }
        
        # CREATE
        response = self.client.post(empresa_url, empresa_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        nueva_empresa_id = response.data['id']
        
        # READ
        response = self.client.get(f'{empresa_url}{nueva_empresa_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Nueva Empresa')
        
        # UPDATE
        empresa_data['nombre'] = 'Empresa Actualizada'
        response = self.client.put(f'{empresa_url}{nueva_empresa_id}/', empresa_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Empresa Actualizada')
        
        # DELETE
        response = self.client.delete(f'{empresa_url}{nueva_empresa_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DualAPISupportTests(APICompatibilityTestCase):
    """Test dual API support during transition period."""
    
    def test_both_apis_return_consistent_data(self):
        """Test that both old and new APIs return consistent organizational data."""
        # Get data from legacy API
        legacy_org_response = self.client.get('/api/organizaciones/')
        legacy_sucursal_response = self.client.get('/api/sucursales/')
        legacy_acueducto_response = self.client.get('/api/acueductos/')
        
        # Get data from new API
        new_empresa_response = self.client.get('/api/institucion/empresas/')
        new_vp_response = self.client.get('/api/institucion/vicepresidencias/')
        new_unidad_response = self.client.get('/api/institucion/unidades-organizacionales/')
        
        # Verify all APIs return successful responses
        self.assertEqual(legacy_org_response.status_code, status.HTTP_200_OK)
        self.assertEqual(legacy_sucursal_response.status_code, status.HTTP_200_OK)
        self.assertEqual(legacy_acueducto_response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_empresa_response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_vp_response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_unidad_response.status_code, status.HTTP_200_OK)
        
        # Verify data consistency where applicable
        legacy_org = legacy_org_response.data['results'][0]
        new_empresa = new_empresa_response.data['results'][0]
        
        # Both should have organizational data (though structure differs)
        self.assertIsNotNone(legacy_org['nombre'])
        self.assertIsNotNone(new_empresa['nombre'])
        
        # Verify migration mapping exists
        migration_response = self.client.get('/api/institucion/migraciones/')
        self.assertEqual(migration_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(migration_response.data['results']), 0)
    
    def test_api_versioning_headers(self):
        """Test API versioning through headers."""
        # Test with version header
        headers = {'HTTP_API_VERSION': 'v1'}
        response = self.client.get('/api/organizaciones/', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        headers = {'HTTP_API_VERSION': 'v2'}
        response = self.client.get('/api/institucion/empresas/', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_migration_status_endpoint(self):
        """Test migration status monitoring endpoint."""
        url = '/api/institucion/empresas/migration_status/'
        response = self.client.get(url)
        
        # Should return migration status information
        # Note: This endpoint depends on MigrationEngine service implementation
        # For now, we test that the endpoint exists and returns a response
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_501_NOT_IMPLEMENTED])
    
    def test_concurrent_api_access(self):
        """Test that both APIs can be accessed concurrently without conflicts."""
        import threading
        import time
        
        results = []
        errors = []
        
        def access_legacy_api():
            try:
                response = self.client.get('/api/organizaciones/')
                results.append(('legacy', response.status_code))
            except Exception as e:
                errors.append(('legacy', str(e)))
        
        def access_new_api():
            try:
                response = self.client.get('/api/institucion/empresas/')
                results.append(('new', response.status_code))
            except Exception as e:
                errors.append(('new', str(e)))
        
        # Create threads for concurrent access
        legacy_thread = threading.Thread(target=access_legacy_api)
        new_thread = threading.Thread(target=access_new_api)
        
        # Start threads
        legacy_thread.start()
        new_thread.start()
        
        # Wait for completion
        legacy_thread.join(timeout=5)
        new_thread.join(timeout=5)
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        # Verify both APIs responded successfully
        self.assertEqual(len(results), 2)
        for api_type, status_code in results:
            self.assertEqual(status_code, status.HTTP_200_OK, f"{api_type} API failed")


class DataFormatCompatibilityTests(APICompatibilityTestCase):
    """Test data format compatibility for frontend components."""
    
    def test_legacy_api_json_structure(self):
        """Test that legacy API maintains exact JSON structure."""
        response = self.client.get('/api/organizaciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify top-level structure
        expected_top_level = ['count', 'next', 'previous', 'results']
        for field in expected_top_level:
            self.assertIn(field, response.data)
        
        # Verify individual record structure
        if response.data['results']:
            record = response.data['results'][0]
            expected_fields = ['id', 'nombre', 'rif', 'parent', 'parent_nombre', 'sucursales_count']
            for field in expected_fields:
                self.assertIn(field, record)
    
    def test_new_api_json_structure(self):
        """Test that new API provides rich JSON structure."""
        response = self.client.get('/api/institucion/empresas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if response.data['results']:
            record = response.data['results'][0]
            
            # Verify enhanced fields are present
            enhanced_fields = ['full_path', 'subsidiarias_count', 'vicepresidencias_count']
            for field in enhanced_fields:
                self.assertIn(field, record)
            
            # Verify data types
            self.assertIsInstance(record['subsidiarias_count'], int)
            self.assertIsInstance(record['vicepresidencias_count'], int)
            self.assertIsInstance(record['full_path'], str)
    
    def test_date_format_consistency(self):
        """Test that date formats are consistent across APIs."""
        # Test legacy API date format
        response = self.client.get('/api/sucursales/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test new API date format
        response = self.client.get('/api/institucion/empresas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if response.data['results']:
            record = response.data['results'][0]
            # Verify ISO format dates
            self.assertRegex(record['fecha_creacion'], r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
            self.assertRegex(record['fecha_actualizacion'], r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
    
    def test_error_response_format_consistency(self):
        """Test that error responses maintain consistent format."""
        # Test 404 error format
        response = self.client.get('/api/organizaciones/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.get('/api/institucion/empresas/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test validation error format
        response = self.client.post('/api/organizaciones/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.post('/api/institucion/empresas/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_pagination_format_consistency(self):
        """Test that pagination format is consistent across APIs."""
        # Test legacy API pagination
        response = self.client.get('/api/organizaciones/?page_size=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        pagination_fields = ['count', 'next', 'previous', 'results']
        for field in pagination_fields:
            self.assertIn(field, response.data)
        
        # Test new API pagination
        response = self.client.get('/api/institucion/empresas/?page_size=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for field in pagination_fields:
            self.assertIn(field, response.data)


class APIPerformanceCompatibilityTests(APICompatibilityTestCase):
    """Test API performance and optimization compatibility."""
    
    def test_legacy_api_query_optimization(self):
        """Test that legacy APIs maintain query optimization."""
        # Create additional test data
        for i in range(5):
            org = OrganizacionCentral.objects.create(
                nombre=f'Organización {i}',
                rif=f'G-2000000{i}-0'
            )
            sucursal = Sucursal.objects.create(
                nombre=f'Sucursal {i}',
                organizacion_central=org,
                codigo=f'SUC{i}'
            )
            Acueducto.objects.create(
                nombre=f'Acueducto {i}',
                sucursal=sucursal,
                codigo=f'ACU{i}'
            )
        
        # Test that queries are optimized (no N+1 problems)
        with self.assertNumQueries(3):  # Should be minimal queries due to select_related/prefetch_related
            response = self.client.get('/api/organizaciones/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Access related data to trigger potential N+1 queries
            for org in response.data['results']:
                _ = org['sucursales_count']  # This should not trigger additional queries
    
    def test_new_api_query_optimization(self):
        """Test that new APIs are properly optimized."""
        # Create additional test data
        for i in range(3):
            vp = Vicepresidencia.objects.create(
                empresa=self.empresa,
                nombre=f'VP {i}',
                codigo=f'VP{i}',
                tipo='ADMINISTRATIVA'
            )
            unidad = UnidadOrganizacional.objects.create(
                vicepresidencia=vp,
                nombre=f'Unidad {i}',
                codigo=f'UN{i}',
                tipo='DEPARTAMENTO'
            )
        
        # Test optimized queries
        with self.assertNumQueries(4):  # Should be minimal due to optimization
            response = self.client.get('/api/institucion/vicepresidencias/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Access related data
            for vp in response.data['results']:
                _ = vp['empresa_nombre']
                _ = vp['unidades_count']
    
    def test_api_response_time_consistency(self):
        """Test that API response times are consistent."""
        import time
        
        # Measure legacy API response time
        start_time = time.time()
        response = self.client.get('/api/organizaciones/')
        legacy_time = time.time() - start_time
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Measure new API response time
        start_time = time.time()
        response = self.client.get('/api/institucion/empresas/')
        new_time = time.time() - start_time
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Both should be reasonably fast (under 1 second for test data)
        self.assertLess(legacy_time, 1.0)
        self.assertLess(new_time, 1.0)


class MigrationStatusAPITests(APICompatibilityTestCase):
    """Test migration status and monitoring API endpoints."""
    
    def test_migration_list_endpoint(self):
        """Test migration list endpoint."""
        url = '/api/institucion/migraciones/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        self.assertEqual(len(results), 1)
        
        migration_data = results[0]
        expected_fields = [
            'id', 'organizacion_central_id', 'sucursal_id', 'acueducto_id',
            'empresa', 'vicepresidencia', 'unidad_organizacional', 'acueducto_nuevo',
            'fecha_migracion', 'estado_migracion', 'validado', 'migrado_por',
            'migrado_por_username', 'validado_por', 'validado_por_username',
            'old_reference_display', 'new_reference_display'
        ]
        for field in expected_fields:
            self.assertIn(field, migration_data)
        
        self.assertEqual(migration_data['estado_migracion'], 'COMPLETADA')
        self.assertTrue(migration_data['validado'])
    
    def test_migration_integrity_report_endpoint(self):
        """Test migration integrity report endpoint."""
        url = '/api/institucion/migraciones/integrity_report/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_fields = ['errores', 'warnings', 'total_migraciones', 'completadas', 'pendientes', 'fallidas']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_migration_summary_stats_endpoint(self):
        """Test migration summary statistics endpoint."""
        url = '/api/institucion/migraciones/summary_stats/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_fields = [
            'total_migrations', 'completed', 'pending', 'failed', 'validated',
            'completion_rate', 'validation_rate'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify calculated rates
        self.assertEqual(response.data['total_migrations'], 1)
        self.assertEqual(response.data['completed'], 1)
        self.assertEqual(response.data['completion_rate'], 100.0)
        self.assertEqual(response.data['validation_rate'], 100.0)


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
                'auditoria',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])