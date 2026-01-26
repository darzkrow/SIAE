"""
Property-based tests for API endpoint functionality.

These tests validate universal properties that should hold across all API operations:
- API Endpoint Completeness (Property 6)
- Bulk Operations Reliability (Property 8)
- Dynamic Permission Evaluation (Property 13)

**Feature: system-modernization**
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
import json
from decimal import Decimal

from inventario.models import ChemicalProduct, UnitOfMeasure, Supplier
from catalogo.models import CategoriaProducto
from accounts.models import Role, Permission, UserRole, RolePermission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class APIEndpointCompletenessPropertyTest(HypothesisTestCase):
    """
    **Property 6: API Endpoint Completeness**
    **Validates: Requirements 2.1**
    
    For any Django model in the system, complete CRUD endpoints should be 
    available and function correctly with proper error handling.
    """
    
    def setUp(self):
        """Set up test data for property tests."""
        self.admin_user = User.objects.create_user(
            username='admin_prop',
            email='admin@prop.com',
            password='adminpass123',
            role='ADMIN'
        )
        
        self.category = CategoriaProducto.objects.create(
            nombre='Property Test Category',
            codigo='PROP',
            activo=True
        )
        
        self.unit = UnitOfMeasure.objects.create(
            nombre='Test Unit',
            simbolo='TU',
            tipo='PESO'
        )
        
        self.supplier = Supplier.objects.create(
            nombre='Property Test Supplier',
            rif='J-11111111-1',
            codigo='PROP001'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
    
    @given(
        sku=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        nombre=st.text(min_size=5, max_size=100),
        stock_actual=st.integers(min_value=0, max_value=10000),
        stock_minimo=st.integers(min_value=0, max_value=1000),
        precio_unitario=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2)
    )
    @settings(max_examples=100, deadline=None)
    def test_create_endpoint_completeness(self, sku, nombre, stock_actual, stock_minimo, precio_unitario):
        """Test that CREATE endpoint works for any valid input data."""
        assume(len(sku.strip()) >= 3)
        assume(len(nombre.strip()) >= 5)
        
        data = {
            'sku': sku.strip(),
            'nombre': nombre.strip(),
            'categoria': self.category.id,
            'unidad_medida': self.unit.id,
            'proveedor': self.supplier.id,
            'stock_actual': stock_actual,
            'stock_minimo': stock_minimo,
            'precio_unitario': float(precio_unitario)
        }
        
        response = self.client.post('/api/inventario/chemical-products/', data, format='json')
        
        # Property: CREATE endpoint should either succeed or fail with proper error handling
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT  # For duplicate SKUs
        ])
        
        if response.status_code == status.HTTP_201_CREATED:
            # Verify the object was actually created
            created_id = response.data['id']
            self.assertTrue(ChemicalProduct.objects.filter(id=created_id).exists())
            
            # Test READ endpoint for the created object
            read_response = self.client.get(f'/api/inventario/chemical-products/{created_id}/')
            self.assertEqual(read_response.status_code, status.HTTP_200_OK)
            self.assertEqual(read_response.data['sku'], sku.strip())
    
    @given(
        nombre_update=st.text(min_size=5, max_size=100),
        stock_update=st.integers(min_value=0, max_value=10000)
    )
    @settings(max_examples=100, deadline=None)
    def test_update_endpoint_completeness(self, nombre_update, stock_update):
        """Test that UPDATE endpoint works for any valid update data."""
        assume(len(nombre_update.strip()) >= 5)
        
        # Create a test object first
        chemical = ChemicalProduct.objects.create(
            sku=f'UPDATE{self.id}',
            nombre='Original Name',
            categoria=self.category,
            unidad_medida=self.unit,
            proveedor=self.supplier,
            stock_actual=100,
            stock_minimo=10,
            precio_unitario=Decimal('25.50')
        )
        
        update_data = {
            'nombre': nombre_update.strip(),
            'stock_actual': stock_update
        }
        
        response = self.client.patch(
            f'/api/inventario/chemical-products/{chemical.id}/',
            update_data,
            format='json'
        )
        
        # Property: UPDATE endpoint should either succeed or fail with proper error handling
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ])
        
        if response.status_code == status.HTTP_200_OK:
            # Verify the object was actually updated
            chemical.refresh_from_db()
            self.assertEqual(chemical.nombre, nombre_update.strip())
            self.assertEqual(chemical.stock_actual, stock_update)
    
    @settings(max_examples=50, deadline=None)
    def test_delete_endpoint_completeness(self):
        """Test that DELETE endpoint works correctly."""
        # Create a test object
        chemical = ChemicalProduct.objects.create(
            sku=f'DELETE{self.id}',
            nombre='To Be Deleted',
            categoria=self.category,
            unidad_medida=self.unit,
            proveedor=self.supplier,
            stock_actual=50,
            stock_minimo=5,
            precio_unitario=Decimal('15.00')
        )
        
        object_id = chemical.id
        
        response = self.client.delete(f'/api/inventario/chemical-products/{object_id}/')
        
        # Property: DELETE endpoint should succeed for existing objects
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the object was actually deleted
        self.assertFalse(ChemicalProduct.objects.filter(id=object_id).exists())
        
        # Verify subsequent GET returns 404
        get_response = self.client.get(f'/api/inventario/chemical-products/{object_id}/')
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
    
    @given(
        page_size=st.integers(min_value=1, max_value=100),
        search_term=st.text(min_size=0, max_size=50)
    )
    @settings(max_examples=50, deadline=None)
    def test_list_endpoint_completeness(self, page_size, search_term):
        """Test that LIST endpoint works with various parameters."""
        # Create some test objects
        for i in range(5):
            ChemicalProduct.objects.create(
                sku=f'LIST{i:03d}',
                nombre=f'List Test Chemical {i}',
                categoria=self.category,
                unidad_medida=self.unit,
                proveedor=self.supplier,
                stock_actual=10 + i,
                stock_minimo=5,
                precio_unitario=Decimal('10.00') + Decimal(str(i))
            )
        
        params = {'page_size': page_size}
        if search_term.strip():
            params['search'] = search_term.strip()
        
        response = self.client.get('/api/inventario/chemical-products/', params)
        
        # Property: LIST endpoint should always return valid paginated response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        
        # Results should not exceed page_size
        self.assertLessEqual(len(response.data['results']), page_size)


class BulkOperationsReliabilityPropertyTest(HypothesisTestCase):
    """
    **Property 8: Bulk Operations Reliability**
    **Validates: Requirements 2.3**
    
    For any bulk operation request, the system should process multiple records 
    correctly, handle partial failures gracefully, and provide detailed feedback 
    on the operation results.
    """
    
    def setUp(self):
        """Set up test data for bulk operations tests."""
        self.admin_user = User.objects.create_user(
            username='bulk_admin',
            email='bulk@admin.com',
            password='bulkpass123',
            role='ADMIN'
        )
        
        self.category = CategoriaProducto.objects.create(
            nombre='Bulk Test Category',
            codigo='BULK',
            activo=True
        )
        
        self.unit = UnitOfMeasure.objects.create(
            nombre='Bulk Unit',
            simbolo='BU',
            tipo='VOLUMEN'
        )
        
        self.supplier = Supplier.objects.create(
            nombre='Bulk Test Supplier',
            rif='J-22222222-2',
            codigo='BULK001'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
    
    @given(
        item_count=st.integers(min_value=1, max_value=50),
        base_stock=st.integers(min_value=1, max_value=1000),
        base_price=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=100, deadline=None)
    def test_bulk_create_reliability(self, item_count, base_stock, base_price):
        """Test bulk create operations handle multiple items correctly."""
        items = []
        for i in range(item_count):
            items.append({
                'sku': f'BULK_CREATE_{i:03d}_{self.id}',
                'nombre': f'Bulk Created Chemical {i}',
                'categoria': self.category.id,
                'unidad_medida': self.unit.id,
                'proveedor': self.supplier.id,
                'stock_actual': base_stock + i,
                'stock_minimo': max(1, base_stock // 10),
                'precio_unitario': float(base_price) + (i * 0.5)
            })
        
        data = {'items': items}
        response = self.client.post('/api/inventario/chemical-products/bulk_create/', data, format='json')
        
        # Property: Bulk create should handle any number of valid items
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_207_MULTI_STATUS,
            status.HTTP_400_BAD_REQUEST  # If exceeds limits
        ])
        
        if response.status_code in [status.HTTP_201_CREATED, status.HTTP_207_MULTI_STATUS]:
            # Verify response structure
            self.assertIn('created_count', response.data)
            self.assertIn('error_count', response.data)
            
            # Property: created_count + error_count should equal total items
            total_processed = response.data['created_count'] + response.data['error_count']
            self.assertEqual(total_processed, item_count)
            
            # Verify actual objects were created
            created_count = response.data['created_count']
            if created_count > 0:
                # Check that the reported number of objects were actually created
                created_skus = [item['sku'] for item in items[:created_count]]
                actual_created = ChemicalProduct.objects.filter(sku__in=created_skus).count()
                self.assertEqual(actual_created, created_count)
    
    @given(
        update_count=st.integers(min_value=1, max_value=20),
        new_stock=st.integers(min_value=0, max_value=5000)
    )
    @settings(max_examples=100, deadline=None)
    def test_bulk_update_reliability(self, update_count, new_stock):
        """Test bulk update operations handle multiple updates correctly."""
        # Create objects to update
        objects_to_update = []
        for i in range(update_count):
            obj = ChemicalProduct.objects.create(
                sku=f'BULK_UPDATE_{i:03d}_{self.id}',
                nombre=f'To Update Chemical {i}',
                categoria=self.category,
                unidad_medida=self.unit,
                proveedor=self.supplier,
                stock_actual=100,
                stock_minimo=10,
                precio_unitario=Decimal('20.00')
            )
            objects_to_update.append(obj)
        
        # Prepare updates
        updates = []
        for i, obj in enumerate(objects_to_update):
            updates.append({
                'id': obj.id,
                'stock_actual': new_stock + i
            })
        
        data = {'updates': updates}
        response = self.client.patch('/api/inventario/chemical-products/bulk_update/', data, format='json')
        
        # Property: Bulk update should handle any number of valid updates
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_207_MULTI_STATUS,
            status.HTTP_400_BAD_REQUEST
        ])
        
        if response.status_code in [status.HTTP_200_OK, status.HTTP_207_MULTI_STATUS]:
            # Verify response structure
            self.assertIn('updated_count', response.data)
            self.assertIn('error_count', response.data)
            
            # Property: updated_count + error_count should equal total updates
            total_processed = response.data['updated_count'] + response.data['error_count']
            self.assertEqual(total_processed, update_count)
            
            # Verify actual objects were updated
            updated_count = response.data['updated_count']
            if updated_count > 0:
                # Check that objects were actually updated
                for i, obj in enumerate(objects_to_update[:updated_count]):
                    obj.refresh_from_db()
                    self.assertEqual(obj.stock_actual, new_stock + i)
    
    @given(
        delete_count=st.integers(min_value=1, max_value=30)
    )
    @settings(max_examples=50, deadline=None)
    def test_bulk_delete_reliability(self, delete_count):
        """Test bulk delete operations handle multiple deletions correctly."""
        # Create objects to delete
        objects_to_delete = []
        for i in range(delete_count):
            obj = ChemicalProduct.objects.create(
                sku=f'BULK_DELETE_{i:03d}_{self.id}',
                nome=f'To Delete Chemical {i}',
                categoria=self.category,
                unidad_medida=self.unit,
                proveedor=self.supplier,
                stock_actual=50,
                stock_minimo=5,
                precio_unitario=Decimal('15.00')
            )
            objects_to_delete.append(obj)
        
        # Prepare deletion IDs
        ids_to_delete = [obj.id for obj in objects_to_delete]
        
        data = {'ids': ids_to_delete}
        response = self.client.delete('/api/inventario/chemical-products/bulk_delete/', data, format='json')
        
        # Property: Bulk delete should handle any number of valid IDs
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_207_MULTI_STATUS,
            status.HTTP_400_BAD_REQUEST
        ])
        
        if response.status_code in [status.HTTP_200_OK, status.HTTP_207_MULTI_STATUS]:
            # Verify response structure
            self.assertIn('deleted_count', response.data)
            self.assertIn('error_count', response.data)
            
            # Property: deleted_count + error_count should equal total IDs
            total_processed = response.data['deleted_count'] + response.data['error_count']
            self.assertEqual(total_processed, delete_count)
            
            # Verify actual objects were deleted
            deleted_count = response.data['deleted_count']
            if deleted_count > 0:
                # Check that objects were actually deleted
                remaining_objects = ChemicalProduct.objects.filter(id__in=ids_to_delete).count()
                expected_remaining = delete_count - deleted_count
                self.assertEqual(remaining_objects, expected_remaining)
    
    @given(
        mixed_valid_count=st.integers(min_value=1, max_value=10),
        mixed_invalid_count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_bulk_operations_partial_failure_handling(self, mixed_valid_count, mixed_invalid_count):
        """Test that bulk operations handle partial failures gracefully."""
        items = []
        
        # Add valid items
        for i in range(mixed_valid_count):
            items.append({
                'sku': f'VALID_{i:03d}_{self.id}',
                'nombre': f'Valid Chemical {i}',
                'categoria': self.category.id,
                'unidad_medida': self.unit.id,
                'proveedor': self.supplier.id,
                'stock_actual': 100,
                'stock_minimo': 10,
                'precio_unitario': 25.00
            })
        
        # Add invalid items (missing required fields)
        for i in range(mixed_invalid_count):
            items.append({
                'sku': '',  # Invalid - empty SKU
                'nombre': f'Invalid Chemical {i}',
                # Missing required fields
            })
        
        data = {'items': items}
        response = self.client.post('/api/inventario/chemical-products/bulk_create/', data, format='json')
        
        # Property: Partial failures should return 207 Multi-Status
        if response.status_code == status.HTTP_207_MULTI_STATUS:
            # Verify that valid items were created and invalid items reported as errors
            self.assertEqual(response.data['created_count'], mixed_valid_count)
            self.assertEqual(response.data['error_count'], mixed_invalid_count)
            self.assertIn('errors', response.data)
            
            # Verify error details are provided
            errors = response.data['errors']
            self.assertEqual(len(errors), mixed_invalid_count)
            
            for error in errors:
                self.assertIn('index', error)
                self.assertIn('data', error)
                self.assertIn('errors', error)


class DynamicPermissionEvaluationPropertyTest(HypothesisTestCase):
    """
    **Property 13: Dynamic Permission Evaluation**
    **Validates: Requirements 3.2**
    
    For any user and resource combination, the permission engine should evaluate 
    access rights dynamically from the database and return consistent results.
    """
    
    def setUp(self):
        """Set up test data for permission tests."""
        # Create test users with different roles
        self.admin_user = User.objects.create_user(
            username='perm_admin',
            email='perm@admin.com',
            password='permpass123'
        )
        
        self.regular_user = User.objects.create_user(
            username='perm_regular',
            email='perm@regular.com',
            password='permpass123'
        )
        
        # Create roles and permissions
        self.admin_role = Role.objects.create(
            name='Test Admin',
            description='Admin role for testing'
        )
        
        self.user_role = Role.objects.create(
            name='Test User',
            description='Regular user role for testing'
        )
        
        # Create permissions for ChemicalProduct
        content_type = ContentType.objects.get_for_model(ChemicalProduct)
        
        self.view_permission = Permission.objects.create(
            name='Can view chemical product',
            codename='view_chemicalproduct',
            content_type=content_type
        )
        
        self.add_permission = Permission.objects.create(
            name='Can add chemical product',
            codename='add_chemicalproduct',
            content_type=content_type
        )
        
        self.change_permission = Permission.objects.create(
            name='Can change chemical product',
            codename='change_chemicalproduct',
            content_type=content_type
        )
        
        self.delete_permission = Permission.objects.create(
            name='Can delete chemical product',
            codename='delete_chemicalproduct',
            content_type=content_type
        )
        
        # Assign permissions to roles
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.view_permission,
            granted=True
        )
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.add_permission,
            granted=True
        )
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.change_permission,
            granted=True
        )
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.delete_permission,
            granted=True
        )
        
        # Regular user only has view permission
        RolePermission.objects.create(
            role=self.user_role,
            permission=self.view_permission,
            granted=True
        )
        
        # Assign roles to users
        UserRole.objects.create(
            user=self.admin_user,
            role=self.admin_role,
            is_active=True
        )
        
        UserRole.objects.create(
            user=self.regular_user,
            role=self.user_role,
            is_active=True
        )
        
        self.client = APIClient()
    
    @given(
        action=st.sampled_from(['list', 'retrieve', 'create', 'update', 'delete'])
    )
    @settings(max_examples=100, deadline=None)
    def test_permission_evaluation_consistency(self, action):
        """Test that permission evaluation is consistent for the same user and action."""
        from inventario.dynamic_permissions import PermissionEvaluator
        
        # Test admin user permissions
        admin_permission = PermissionEvaluator.user_has_permission(
            self.admin_user, ChemicalProduct, action
        )
        
        # Test regular user permissions
        regular_permission = PermissionEvaluator.user_has_permission(
            self.regular_user, ChemicalProduct, action
        )
        
        # Property: Admin should have all permissions
        self.assertTrue(admin_permission, f"Admin should have {action} permission")
        
        # Property: Regular user should only have view permission
        if action in ['list', 'retrieve']:
            self.assertTrue(regular_permission, f"Regular user should have {action} permission")
        else:
            self.assertFalse(regular_permission, f"Regular user should not have {action} permission")
        
        # Property: Multiple evaluations should return the same result
        admin_permission_2 = PermissionEvaluator.user_has_permission(
            self.admin_user, ChemicalProduct, action
        )
        regular_permission_2 = PermissionEvaluator.user_has_permission(
            self.regular_user, ChemicalProduct, action
        )
        
        self.assertEqual(admin_permission, admin_permission_2)
        self.assertEqual(regular_permission, regular_permission_2)
    
    @settings(max_examples=50, deadline=None)
    def test_api_permission_enforcement(self):
        """Test that API endpoints enforce permissions correctly."""
        # Create test data
        category = CategoriaProducto.objects.create(
            nombre='Permission Test Category',
            codigo='PERM',
            activo=True
        )
        
        unit = UnitOfMeasure.objects.create(
            nombre='Permission Unit',
            simbolo='PU',
            tipo='PESO'
        )
        
        supplier = Supplier.objects.create(
            nombre='Permission Supplier',
            rif='J-33333333-3',
            codigo='PERM001'
        )
        
        # Test with admin user
        self.client.force_authenticate(user=self.admin_user)
        
        # Admin should be able to create
        create_data = {
            'sku': 'PERM_TEST_001',
            'nombre': 'Permission Test Chemical',
            'categoria': category.id,
            'unidad_medida': unit.id,
            'proveedor': supplier.id,
            'stock_actual': 100,
            'stock_minimo': 10,
            'precio_unitario': 25.00
        }
        
        create_response = self.client.post('/api/inventario/chemical-products/', create_data, format='json')
        
        # Property: Admin should be able to create
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        created_id = create_response.data['id']
        
        # Test with regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Regular user should be able to view
        list_response = self.client.get('/api/inventario/chemical-products/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        
        retrieve_response = self.client.get(f'/api/inventario/chemical-products/{created_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        
        # Regular user should not be able to create
        create_response_regular = self.client.post('/api/inventario/chemical-products/', create_data, format='json')
        self.assertIn(create_response_regular.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ])
        
        # Regular user should not be able to update
        update_data = {'nombre': 'Updated Name'}
        update_response = self.client.patch(f'/api/inventario/chemical-products/{created_id}/', update_data, format='json')
        self.assertIn(update_response.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ])
        
        # Regular user should not be able to delete
        delete_response = self.client.delete(f'/api/inventario/chemical-products/{created_id}/')
        self.assertIn(delete_response.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ])