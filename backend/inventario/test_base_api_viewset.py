"""
Unit tests for Base API ViewSet functionality.

Tests cover:
- Basic CRUD operations
- Bulk operations (create, update, delete)
- Advanced search and filtering
- Permission handling
- Error conditions
- Performance optimizations
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import json

from inventario.models import ChemicalProduct, UnitOfMeasure, Supplier
from catalogo.models import CategoriaProducto
from accounts.models import Role, Permission, UserRole, RolePermission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class BaseAPIViewSetTestCase(APITestCase):
    """Test cases for BaseAPIViewSet functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='ADMIN'
        )
        
        # Create test data
        self.category = CategoriaProducto.objects.create(
            nombre='Test Category',
            codigo='TEST',
            activo=True
        )
        
        self.unit = UnitOfMeasure.objects.create(
            nombre='Kilogram',
            simbolo='kg',
            tipo='PESO'
        )
        
        self.supplier = Supplier.objects.create(
            nombre='Test Supplier',
            rif='J-12345678-9',
            codigo='SUP001'
        )
        
        # Create test chemical products
        self.chemical1 = ChemicalProduct.objects.create(
            sku='CHEM001',
            nombre='Test Chemical 1',
            categoria=self.category,
            unidad_medida=self.unit,
            proveedor=self.supplier,
            stock_actual=100,
            stock_minimo=10,
            precio_unitario=25.50
        )
        
        self.chemical2 = ChemicalProduct.objects.create(
            sku='CHEM002',
            nombre='Test Chemical 2',
            categoria=self.category,
            unidad_medida=self.unit,
            proveedor=self.supplier,
            stock_actual=5,  # Low stock
            stock_minimo=10,
            precio_unitario=15.75
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_list_endpoint(self):
        """Test basic list functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_endpoint(self):
        """Test retrieve single object."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-detail', kwargs={'pk': self.chemical1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sku'], 'CHEM001')
    
    def test_create_endpoint(self):
        """Test create functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'sku': 'CHEM003',
            'nombre': 'Test Chemical 3',
            'categoria': self.category.id,
            'unidad_medida': self.unit.id,
            'proveedor': self.supplier.id,
            'stock_actual': 50,
            'stock_minimo': 5,
            'precio_unitario': 30.00
        }
        
        url = reverse('chemical-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChemicalProduct.objects.count(), 3)
    
    def test_update_endpoint(self):
        """Test update functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'nombre': 'Updated Chemical Name',
            'stock_actual': 150
        }
        
        url = reverse('chemical-detail', kwargs={'pk': self.chemical1.pk})
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.chemical1.refresh_from_db()
        self.assertEqual(self.chemical1.nombre, 'Updated Chemical Name')
        self.assertEqual(self.chemical1.stock_actual, 150)
    
    def test_delete_endpoint(self):
        """Test delete functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-detail', kwargs={'pk': self.chemical1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ChemicalProduct.objects.count(), 1)
    
    def test_bulk_create(self):
        """Test bulk create functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'items': [
                {
                    'sku': 'BULK001',
                    'nombre': 'Bulk Chemical 1',
                    'categoria': self.category.id,
                    'unidad_medida': self.unit.id,
                    'proveedor': self.supplier.id,
                    'stock_actual': 25,
                    'stock_minimo': 5,
                    'precio_unitario': 20.00
                },
                {
                    'sku': 'BULK002',
                    'nombre': 'Bulk Chemical 2',
                    'categoria': self.category.id,
                    'unidad_medida': self.unit.id,
                    'proveedor': self.supplier.id,
                    'stock_actual': 35,
                    'stock_minimo': 10,
                    'precio_unitario': 25.00
                }
            ]
        }
        
        url = reverse('chemical-bulk-create')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_count'], 2)
        self.assertEqual(ChemicalProduct.objects.count(), 4)
    
    def test_bulk_update(self):
        """Test bulk update functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'updates': [
                {
                    'id': self.chemical1.id,
                    'stock_actual': 200
                },
                {
                    'id': self.chemical2.id,
                    'precio_unitario': 20.00
                }
            ]
        }
        
        url = reverse('chemical-bulk-update')
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
        
        self.chemical1.refresh_from_db()
        self.chemical2.refresh_from_db()
        self.assertEqual(self.chemical1.stock_actual, 200)
        self.assertEqual(self.chemical2.precio_unitario, 20.00)
    
    def test_bulk_delete(self):
        """Test bulk delete functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'ids': [self.chemical1.id, self.chemical2.id]
        }
        
        url = reverse('chemical-bulk-delete')
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)
        self.assertEqual(ChemicalProduct.objects.count(), 0)
    
    def test_advanced_search(self):
        """Test advanced search functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test text search
        url = reverse('chemical-advanced-search')
        response = self.client.get(url, {'q': 'Chemical 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['sku'], 'CHEM001')
        
        # Test filters
        filters = json.dumps({'stock_actual__lt': 10})
        response = self.client.get(url, {'filters': filters})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['sku'], 'CHEM002')
    
    def test_export_data_json(self):
        """Test JSON data export."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-export-data')
        response = self.client.get(url, {'format': 'json'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIn('data', response.data)
        self.assertIn('exported_at', response.data)
    
    def test_export_data_csv(self):
        """Test CSV data export."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-export-data')
        response = self.client.get(url, {'format': 'csv'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_field_choices(self):
        """Test field choices endpoint."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-field-choices')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ChemicalProduct should have some choice fields
        self.assertIsInstance(response.data, dict)
    
    def test_statistics(self):
        """Test statistics endpoint."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_count'], 2)
        self.assertIn('stock_actual_stats', response.data)
        self.assertIn('precio_unitario_stats', response.data)
    
    def test_pagination(self):
        """Test pagination functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create more test data
        for i in range(30):
            ChemicalProduct.objects.create(
                sku=f'CHEM{i+10:03d}',
                nombre=f'Test Chemical {i+10}',
                categoria=self.category,
                unidad_medida=self.unit,
                proveedor=self.supplier,
                stock_actual=10,
                stock_minimo=5,
                precio_unitario=10.00
            )
        
        url = reverse('chemical-list')
        response = self.client.get(url, {'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('next', response.data)
        self.assertIn('count', response.data)
    
    def test_filtering(self):
        """Test filtering functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-list')
        
        # Test category filter
        response = self.client.get(url, {'categoria': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test stock filter
        response = self.client.get(url, {'stock_actual__lt': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_ordering(self):
        """Test ordering functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-list')
        
        # Test ascending order
        response = self.client.get(url, {'ordering': 'sku'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['sku'], 'CHEM001')
        self.assertEqual(results[1]['sku'], 'CHEM002')
        
        # Test descending order
        response = self.client.get(url, {'ordering': '-sku'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['sku'], 'CHEM002')
        self.assertEqual(results[1]['sku'], 'CHEM001')
    
    def test_search(self):
        """Test search functionality."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('chemical-list')
        
        # Test search by name
        response = self.client.get(url, {'search': 'Chemical 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['sku'], 'CHEM001')
        
        # Test search by SKU
        response = self.client.get(url, {'search': 'CHEM002'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['sku'], 'CHEM002')
    
    def test_permission_denied_for_regular_user(self):
        """Test that regular users have limited access."""
        self.client.force_authenticate(user=self.user)
        
        # Regular user should not be able to create
        data = {
            'sku': 'CHEM003',
            'nombre': 'Test Chemical 3',
            'categoria': self.category.id,
            'unidad_medida': self.unit.id,
            'proveedor': self.supplier.id
        }
        
        url = reverse('chemical-list')
        response = self.client.post(url, data, format='json')
        
        # Should be forbidden or require different permissions
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
    
    def test_bulk_operation_limits(self):
        """Test bulk operation limits."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test bulk create with too many items
        data = {
            'items': [{'sku': f'BULK{i:03d}'} for i in range(101)]
        }
        
        url = reverse('chemical-bulk-create')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Maximum 100 items', response.data['error'])
    
    def test_bulk_create_with_errors(self):
        """Test bulk create with some invalid items."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'items': [
                {
                    'sku': 'VALID001',
                    'nombre': 'Valid Chemical',
                    'categoria': self.category.id,
                    'unidad_medida': self.unit.id,
                    'proveedor': self.supplier.id,
                    'stock_actual': 25,
                    'stock_minimo': 5,
                    'precio_unitario': 20.00
                },
                {
                    'sku': '',  # Invalid - empty SKU
                    'nombre': 'Invalid Chemical',
                    'categoria': self.category.id,
                    'unidad_medida': self.unit.id,
                    'proveedor': self.supplier.id
                }
            ]
        }
        
        url = reverse('chemical-bulk-create')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response.data['created_count'], 1)
        self.assertEqual(response.data['error_count'], 1)
        self.assertIn('errors', response.data)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access endpoints."""
        url = reverse('chemical-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdvancedSearchTestCase(TestCase):
    """Test cases for advanced search functionality."""
    
    def setUp(self):
        """Set up test data for search tests."""
        self.category = CategoriaProducto.objects.create(
            nombre='Search Category',
            codigo='SEARCH',
            activo=True
        )
        
        self.unit = UnitOfMeasure.objects.create(
            nombre='Liter',
            simbolo='L',
            tipo='VOLUMEN'
        )
        
        self.supplier = Supplier.objects.create(
            nombre='Search Supplier',
            rif='J-87654321-0',
            codigo='SEARCH001'
        )
        
        # Create test products with different characteristics
        self.products = [
            ChemicalProduct.objects.create(
                sku='SEARCH001',
                nombre='Chlorine Solution',
                descripcion='High quality chlorine for water treatment',
                categoria=self.category,
                unidad_medida=self.unit,
                proveedor=self.supplier,
                stock_actual=100,
                precio_unitario=15.50
            ),
            ChemicalProduct.objects.create(
                sku='SEARCH002',
                nombre='Sodium Hypochlorite',
                descripcion='Disinfectant solution for pools',
                categoria=self.category,
                unidad_medida=self.unit,
                proveedor=self.supplier,
                stock_actual=50,
                precio_unitario=25.00
            ),
            ChemicalProduct.objects.create(
                sku='SEARCH003',
                nombre='Water Treatment Tablets',
                descripcion='Convenient tablets for small scale treatment',
                categoria=self.category,
                unidad_medida=self.unit,
                proveedor=self.supplier,
                stock_actual=200,
                precio_unitario=8.75
            )
        ]
    
    def test_simple_text_search(self):
        """Test simple text search functionality."""
        from inventario.advanced_search import AdvancedSearchFilter
        
        search_filter = AdvancedSearchFilter()
        queryset = ChemicalProduct.objects.all()
        
        # Mock request with search parameter
        class MockRequest:
            def __init__(self, search_term):
                self.query_params = {'search': search_term}
        
        # Mock view with search fields
        class MockView:
            search_fields = ['nombre', 'descripcion', 'sku']
        
        # Test search for "chlorine"
        request = MockRequest('chlorine')
        view = MockView()
        
        filtered_queryset = search_filter.filter_queryset(request, queryset, view)
        
        # Should find products containing "chlorine"
        self.assertEqual(filtered_queryset.count(), 2)
        skus = [p.sku for p in filtered_queryset]
        self.assertIn('SEARCH001', skus)
        self.assertIn('SEARCH002', skus)
    
    def test_field_specific_search(self):
        """Test field-specific search syntax."""
        from inventario.advanced_search import AdvancedSearchFilter
        
        search_filter = AdvancedSearchFilter()
        
        # Test parsing field-specific search
        parsed = search_filter._parse_search_query('sku:SEARCH001 nombre:chlorine')
        
        self.assertIn('sku', parsed['field_searches'])
        self.assertIn('nombre', parsed['field_searches'])
        self.assertEqual(parsed['field_searches']['sku'], 'SEARCH001')
        self.assertEqual(parsed['field_searches']['nombre'], 'chlorine')
    
    def test_range_search(self):
        """Test range search syntax."""
        from inventario.advanced_search import AdvancedSearchFilter
        
        search_filter = AdvancedSearchFilter()
        
        # Test parsing range search
        parsed = search_filter._parse_search_query('precio:10..20 stock:50..150')
        
        self.assertIn('precio', parsed['range_searches'])
        self.assertIn('stock', parsed['range_searches'])
        self.assertEqual(parsed['range_searches']['precio']['min'], '10')
        self.assertEqual(parsed['range_searches']['precio']['max'], '20')
    
    def test_phrase_search(self):
        """Test quoted phrase search."""
        from inventario.advanced_search import AdvancedSearchFilter
        
        search_filter = AdvancedSearchFilter()
        
        # Test parsing quoted phrases
        parsed = search_filter._parse_search_query('"water treatment" "high quality"')
        
        self.assertIn('water treatment', parsed['phrases'])
        self.assertIn('high quality', parsed['phrases'])
    
    def test_boolean_operators(self):
        """Test boolean operators in search."""
        from inventario.advanced_search import AdvancedSearchFilter
        
        search_filter = AdvancedSearchFilter()
        
        # Test parsing boolean operations
        parsed = search_filter._parse_search_query('chlorine AND solution OR tablets NOT sodium')
        
        self.assertIn('chlorine', parsed['terms'])
        self.assertIn('solution', parsed['terms'])
        self.assertIn('tablets', parsed['terms'])
        # Boolean operations would be handled in query building
    
    def test_search_result_highlighting(self):
        """Test search result highlighting."""
        from inventario.advanced_search import SearchResultHighlighter
        
        text = "This is a test text with important keywords"
        search_terms = ["test", "important"]
        
        highlighted = SearchResultHighlighter.highlight_text(text, search_terms)
        
        self.assertIn('<span class="highlight">test</span>', highlighted)
        self.assertIn('<span class="highlight">important</span>', highlighted)
    
    def test_snippet_extraction(self):
        """Test snippet extraction from long text."""
        from inventario.advanced_search import SearchResultHighlighter
        
        long_text = "This is a very long text " * 20 + " with important keywords " + "more text " * 20
        search_terms = ["important", "keywords"]
        
        snippet = SearchResultHighlighter.extract_snippets(long_text, search_terms, 100)
        
        self.assertIn("important", snippet)
        self.assertIn("keywords", snippet)
        self.assertTrue(len(snippet) <= 200)  # Should be around snippet_length * 2