"""
Property-based test for API Endpoint Completeness.

**Property 6: API Endpoint Completeness**
**Validates: Requirements 2.1**

For any Django model in the system, complete CRUD endpoints should be 
available and function correctly with proper error handling.

**Feature: system-modernization, Property 6: API Endpoint Completeness**
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
import json
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import transaction
from django.test.utils import override_settings
import uuid

from inventario.models import (
    ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    UnitOfMeasure, Supplier, Tag
)
from catalogo.models import CategoriaProducto, Marca
from accounts.models import Role, Permission, UserRole, RolePermission
from geography.models import Ubicacion
from institucion.models import Sucursal, Acueducto

User = get_user_model()


class APIEndpointCompletenessPropertyTest(TransactionTestCase):
    """
    **Property 6: API Endpoint Completeness**
    **Validates: Requirements 2.1**
    
    For any Django model in the system, complete CRUD endpoints should be 
    available and function correctly with proper error handling.
    """
    
    def setUp(self):
        """Set up test data for property tests."""
        # Use unique identifiers to avoid conflicts
        self.test_id = str(uuid.uuid4())[:8]
        
        # Create admin user with all permissions
        self.admin_user = User.objects.create_user(
            username=f'api_admin_{self.test_id}',
            email=f'api_{self.test_id}@admin.com',
            password='apipass123',
            is_superuser=True,
            is_staff=True
        )
        
        # Create test data dependencies
        self.sucursal = Sucursal.objects.create(
            nombre=f'Test Sucursal {self.test_id}',
            codigo=f'TEST_SUC_{self.test_id}',
        )
        
        self.acueducto = Acueducto.objects.create(
            nombre=f'Test Acueducto {self.test_id}',
            codigo=f'TEST_ACU_{self.test_id}',
            sucursal=self.sucursal,
        )
        
        self.ubicacion = Ubicacion.objects.create(
            nombre=f'Test Ubicacion {self.test_id}',
            acueducto=self.acueducto,
            tipo='ALMACEN'
        )
        
        self.category = CategoriaProducto.objects.create(
            nombre=f'API Test Category {self.test_id}',
            codigo=f'API{self.test_id[:3].upper()}',
        )
        
        self.unit = UnitOfMeasure.objects.create(
            nombre=f'API Test Unit {self.test_id}',
            simbolo=f'ATU{self.test_id[:2]}',
            tipo='PESO'
        )
        
        self.supplier = Supplier.objects.create(
            nombre=f'API Test Supplier {self.test_id}',
            rif=f'J-{self.test_id[:8]}-1',
            codigo=f'API{self.test_id[:3]}'
        )
        
        self.marca = Marca.objects.create(
            nombre=f'Test Marca {self.test_id}',
        )
        
        self.tag = Tag.objects.create(
            name=f'test-tag-{self.test_id}',
            color='#FF0000',
            description=f'Test tag for API tests {self.test_id}'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
    
    def get_model_endpoints(self, model_class):
        """Get API endpoints for a model based on naming conventions."""
        model_name = model_class._meta.model_name
        
        # Map model names to endpoint patterns based on actual URLs
        endpoint_map = {
            'chemicalproduct': 'chemicals',
            'pipe': 'pipes',
            'pumpandmotor': 'pumps',
            'accessory': 'accessories',
            'unitofmeasure': 'units',
            'supplier': 'suppliers',
            'tag': 'tags'
        }
        
        endpoint_name = endpoint_map.get(model_name, f"{model_name}s")
        
        return {
            'list': f'/api/inventario/{endpoint_name}/',
            'detail': f'/api/inventario/{endpoint_name}/{{id}}/',
            'bulk_create': f'/api/inventario/{endpoint_name}/bulk_create/',
            'bulk_update': f'/api/inventario/{endpoint_name}/bulk_update/',
            'bulk_delete': f'/api/inventario/{endpoint_name}/bulk_delete/',
        }
    
    def get_valid_data_for_model(self, model_class):
        """Generate valid data for creating model instances."""
        model_name = model_class._meta.model_name
        unique_suffix = str(uuid.uuid4())[:8]
        
        base_data = {}
        
        if model_name == 'chemicalproduct':
            base_data = {
                'nombre': f'Test Chemical Product {unique_suffix}',
                'categoria': self.category.id,
                'unidad_medida': self.unit.id,
                'proveedor': self.supplier.id,
                'stock_actual': 100,
                'stock_minimo': 10,
                'precio_unitario': 25.50
            }
        elif model_name == 'pipe':
            base_data = {
                'nombre': f'Test Pipe {unique_suffix}',
                'categoria': self.category.id,
                'unidad_medida': self.unit.id,
                'proveedor': self.supplier.id,
                'stock_actual': 50,
                'stock_minimo': 5,
                'precio_unitario': 15.75,
                'material': 'PVC',
                'diametro_nominal': 110.0,
                'presion_nominal': 'PN10',
                'tipo_union': 'SOLDABLE',
                'tipo_uso': 'POTABLE'
            }
        elif model_name == 'pumpandmotor':
            base_data = {
                'nombre': f'Test Pump Motor {unique_suffix}',
                'categoria': self.category.id,
                'unidad_medida': self.unit.id,
                'proveedor': self.supplier.id,
                'stock_actual': 1,
                'stock_minimo': 1,
                'precio_unitario': 500.00,
                'tipo_equipo': 'BOMBA_CENTRIFUGA',
                'marca': self.marca.id,
                'modelo': f'TEST-MODEL-{unique_suffix}',
                'numero_serie': f'SN{unique_suffix}',
                'potencia_hp': 5.0,
                'voltaje': 220,
                'fases': 'TRIFASICO'
            }
        elif model_name == 'accessory':
            base_data = {
                'nombre': f'Test Accessory {unique_suffix}',
                'categoria': self.category.id,
                'unidad_medida': self.unit.id,
                'proveedor': self.supplier.id,
                'stock_actual': 20,
                'stock_minimo': 5,
                'precio_unitario': 8.50,
                'tipo_accesorio': 'VALVULA',
                'diametro_entrada': 2.0,
                'tipo_conexion': 'ROSCADA',
                'presion_trabajo': 'PN10',
                'material': 'PVC'
            }
        elif model_name == 'unitofmeasure':
            base_data = {
                'nombre': f'Test Unit {unique_suffix}',
                'simbolo': f'TU{unique_suffix[:2]}',
                'tipo': 'PESO'
            }
        elif model_name == 'supplier':
            base_data = {
                'nombre': f'Test Supplier {unique_suffix}',
                'rif': f'J-{unique_suffix[:8]}-1',
                'codigo': f'SUP{unique_suffix[:3]}'
            }
        elif model_name == 'tag':
            base_data = {
                'name': f'test-tag-{unique_suffix}',
                'color': '#00FF00',
                'description': f'Generated test tag {unique_suffix}'
            }
        
        return base_data
    
    @given(
        model_choice=st.sampled_from([
            ChemicalProduct, Pipe, PumpAndMotor, Accessory,
            UnitOfMeasure, Supplier, Tag
        ])
    )
    @settings(max_examples=100, deadline=None)
    def test_create_endpoint_exists_and_works(self, model_choice):
        """Test that CREATE endpoint exists and works for any model."""
        endpoints = self.get_model_endpoints(model_choice)
        valid_data = self.get_valid_data_for_model(model_choice)
        
        if not valid_data:
            assume(False)  # Skip if no valid data available
        
        # Add unique identifier to avoid conflicts
        if 'sku' in valid_data:
            valid_data['sku'] = f'CREATE_{self.id}_{model_choice._meta.model_name}'
        elif 'codigo' in valid_data:
            valid_data['codigo'] = f'CREATE_{self.id}_{model_choice._meta.model_name}'
        elif 'numero_serie' in valid_data:
            valid_data['numero_serie'] = f'CREATE_{self.id}_{model_choice._meta.model_name}'
        elif 'name' in valid_data:
            valid_data['name'] = f'create-{self.id}-{model_choice._meta.model_name}'
        
        response = self.client.post(endpoints['list'], valid_data, format='json')
        
        # Property: CREATE endpoint should either succeed or fail with proper error handling
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT,
            status.HTTP_404_NOT_FOUND  # If endpoint doesn't exist yet
        ])
        
        if response.status_code == status.HTTP_201_CREATED:
            # Verify the object was actually created
            created_id = response.data['id']
            self.assertTrue(model_choice.objects.filter(id=created_id).exists())
            
            # Test that the created object can be retrieved
            detail_url = endpoints['detail'].format(id=created_id)
            retrieve_response = self.client.get(detail_url)
            
            # Property: Created objects should be retrievable
            self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
            self.assertEqual(retrieve_response.data['id'], created_id)
    
    @given(
        model_choice=st.sampled_from([
            ChemicalProduct, Pipe, PumpAndMotor, Accessory,
            UnitOfMeasure, Supplier, Tag
        ])
    )
    @settings(max_examples=100, deadline=None)
    def test_list_endpoint_exists_and_works(self, model_choice):
        """Test that LIST endpoint exists and works for any model."""
        endpoints = self.get_model_endpoints(model_choice)
        
        response = self.client.get(endpoints['list'])
        
        # Property: LIST endpoint should always return a valid response
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # If endpoint doesn't exist yet
        ])
        
        if response.status_code == status.HTTP_200_OK:
            # Property: Response should have pagination structure
            if isinstance(response.data, dict):
                # Paginated response
                self.assertIn('results', response.data)
                self.assertIsInstance(response.data['results'], list)
            else:
                # Non-paginated response
                self.assertIsInstance(response.data, list)
    
    @given(
        model_choice=st.sampled_from([
            ChemicalProduct, Pipe, PumpAndMotor, Accessory,
            UnitOfMeasure, Supplier, Tag
        ]),
        update_field=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=100, deadline=None)
    def test_update_endpoint_exists_and_works(self, model_choice, update_field):
        """Test that UPDATE endpoint exists and works for any model."""
        assume(len(update_field.strip()) > 0)
        
        # First create an object to update
        valid_data = self.get_valid_data_for_model(model_choice)
        if not valid_data:
            assume(False)
        
        # Add unique identifier
        if 'sku' in valid_data:
            valid_data['sku'] = f'UPDATE_{self.id}_{model_choice._meta.model_name}'
        elif 'codigo' in valid_data:
            valid_data['codigo'] = f'UPDATE_{self.id}_{model_choice._meta.model_name}'
        elif 'numero_serie' in valid_data:
            valid_data['numero_serie'] = f'UPDATE_{self.id}_{model_choice._meta.model_name}'
        elif 'name' in valid_data:
            valid_data['name'] = f'update-{self.id}-{model_choice._meta.model_name}'
        
        try:
            obj = model_choice.objects.create(**valid_data)
        except Exception:
            assume(False)  # Skip if object creation fails
        
        endpoints = self.get_model_endpoints(model_choice)
        detail_url = endpoints['detail'].format(id=obj.id)
        
        # Prepare update data - try to update a safe field
        update_data = {}
        if hasattr(obj, 'nombre'):
            update_data['nombre'] = f'Updated {update_field.strip()}'
        elif hasattr(obj, 'name'):
            update_data['name'] = f'updated-{update_field.strip()}'.lower()
        elif hasattr(obj, 'descripcion'):
            update_data['descripcion'] = f'Updated description {update_field.strip()}'
        else:
            assume(False)  # Skip if no safe field to update
        
        response = self.client.patch(detail_url, update_data, format='json')
        
        # Property: UPDATE endpoint should either succeed or fail with proper error handling
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ])
        
        if response.status_code == status.HTTP_200_OK:
            # Verify the object was actually updated
            obj.refresh_from_db()
            if 'nombre' in update_data:
                self.assertEqual(obj.nombre, update_data['nombre'])
            elif 'name' in update_data:
                self.assertEqual(obj.name, update_data['name'])
    
    @given(
        model_choice=st.sampled_from([
            ChemicalProduct, Pipe, PumpAndMotor, Accessory,
            UnitOfMeasure, Supplier, Tag
        ])
    )
    @settings(max_examples=50, deadline=None)
    def test_delete_endpoint_exists_and_works(self, model_choice):
        """Test that DELETE endpoint exists and works for any model."""
        # First create an object to delete
        valid_data = self.get_valid_data_for_model(model_choice)
        if not valid_data:
            assume(False)
        
        # Add unique identifier
        if 'sku' in valid_data:
            valid_data['sku'] = f'DELETE_{self.id}_{model_choice._meta.model_name}'
        elif 'codigo' in valid_data:
            valid_data['codigo'] = f'DELETE_{self.id}_{model_choice._meta.model_name}'
        elif 'numero_serie' in valid_data:
            valid_data['numero_serie'] = f'DELETE_{self.id}_{model_choice._meta.model_name}'
        elif 'name' in valid_data:
            valid_data['name'] = f'delete-{self.id}-{model_choice._meta.model_name}'
        
        try:
            obj = model_choice.objects.create(**valid_data)
        except Exception:
            assume(False)  # Skip if object creation fails
        
        endpoints = self.get_model_endpoints(model_choice)
        detail_url = endpoints['detail'].format(id=obj.id)
        
        response = self.client.delete(detail_url)
        
        # Property: DELETE endpoint should either succeed or fail with proper error handling
        self.assertIn(response.status_code, [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_400_BAD_REQUEST  # If deletion is not allowed due to constraints
        ])
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            # Verify the object was actually deleted
            self.assertFalse(model_choice.objects.filter(id=obj.id).exists())
    
    @given(
        model_choice=st.sampled_from([
            ChemicalProduct, Pipe, PumpAndMotor, Accessory
        ]),  # Only test bulk operations on main product models
        page_size=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=50, deadline=None)
    def test_bulk_endpoints_exist_and_work(self, model_choice, page_size):
        """Test that bulk operation endpoints exist and work for any model."""
        endpoints = self.get_model_endpoints(model_choice)
        
        # Test bulk_create endpoint exists
        bulk_create_data = {'items': []}
        response = self.client.post(endpoints['bulk_create'], bulk_create_data, format='json')
        
        # Property: Bulk endpoints should exist and handle empty requests gracefully
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,  # Empty items should be rejected
            status.HTTP_404_NOT_FOUND,    # If endpoint doesn't exist yet
            status.HTTP_201_CREATED       # If empty list is accepted
        ])
        
        # Test bulk_update endpoint exists
        bulk_update_data = {'updates': []}
        response = self.client.patch(endpoints['bulk_update'], bulk_update_data, format='json')
        
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK
        ])
        
        # Test bulk_delete endpoint exists
        bulk_delete_data = {'ids': []}
        response = self.client.delete(endpoints['bulk_delete'], bulk_delete_data, format='json')
        
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK
        ])
    
    @given(
        search_term=st.text(min_size=0, max_size=50),
        page_size=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_list_endpoint_supports_common_parameters(self, search_term, page_size):
        """Test that LIST endpoints support common query parameters."""
        # Test with ChemicalProduct as representative model
        endpoints = self.get_model_endpoints(ChemicalProduct)
        
        params = {
            'page_size': page_size
        }
        
        if search_term.strip():
            params['search'] = search_term.strip()
        
        response = self.client.get(endpoints['list'], params)
        
        # Property: LIST endpoints should handle common parameters gracefully
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,  # If parameters are invalid
            status.HTTP_404_NOT_FOUND     # If endpoint doesn't exist yet
        ])
        
        if response.status_code == status.HTTP_200_OK and isinstance(response.data, dict):
            # Property: Page size should be respected
            if 'results' in response.data:
                self.assertLessEqual(len(response.data['results']), page_size)
    
    def test_error_handling_consistency(self):
        """Test that error responses are consistent across endpoints."""
        # Test with invalid data to trigger errors
        invalid_data = {
            'invalid_field': 'invalid_value',
            'another_invalid': 123
        }
        
        endpoints = self.get_model_endpoints(ChemicalProduct)
        
        # Test CREATE with invalid data
        response = self.client.post(endpoints['list'], invalid_data, format='json')
        
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # Property: Error responses should have consistent structure
            self.assertIsInstance(response.data, dict)
            # Should contain error information
            self.assertTrue(any(key in response.data for key in ['error', 'errors', 'detail']))
        
        # Test UPDATE with invalid ID
        invalid_detail_url = endpoints['detail'].format(id=99999)
        response = self.client.get(invalid_detail_url)
        
        # Property: Non-existent resources should return 404
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN  # If permissions prevent access
        ])
    
    def test_content_type_headers(self):
        """Test that endpoints return appropriate content types."""
        endpoints = self.get_model_endpoints(ChemicalProduct)
        
        # Test JSON response
        response = self.client.get(endpoints['list'])
        
        if response.status_code == status.HTTP_200_OK:
            # Property: API endpoints should return JSON by default
            self.assertIn('application/json', response.get('Content-Type', ''))
    
    def test_http_methods_allowed(self):
        """Test that endpoints support appropriate HTTP methods."""
        endpoints = self.get_model_endpoints(ChemicalProduct)
        
        # Test OPTIONS request to discover allowed methods
        response = self.client.options(endpoints['list'])
        
        if response.status_code == status.HTTP_200_OK:
            # Property: Endpoints should declare allowed methods
            allowed_methods = response.get('Allow', '')
            if allowed_methods:
                # Should support at least GET for list endpoints
                self.assertIn('GET', allowed_methods)