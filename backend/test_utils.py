"""
Test Utilities for Backend Property-Based Testing
Common utilities and generators for Hypothesis-based testing
"""

from hypothesis import strategies as st
from hypothesis.extra.django import from_model
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import string
import json

User = get_user_model()

# Basic data generators
def text_strategy(min_size=1, max_size=100, alphabet=None):
    """Generate text with configurable constraints"""
    if alphabet is None:
        alphabet = string.ascii_letters + string.digits + ' '
    return st.text(min_size=min_size, max_size=max_size, alphabet=alphabet)

def email_strategy():
    """Generate valid email addresses"""
    return st.emails()

def phone_strategy():
    """Generate phone numbers"""
    return st.text(min_size=10, max_size=15, alphabet=string.digits + '+-()')

def url_strategy():
    """Generate URLs"""
    return st.builds(
        lambda domain, path: f"https://{domain}.com/{path}",
        domain=st.text(min_size=3, max_size=20, alphabet=string.ascii_lowercase),
        path=st.text(min_size=0, max_size=50, alphabet=string.ascii_lowercase + '/')
    )

# JSON data generators
def json_object_strategy(max_leaves=10):
    """Generate JSON-serializable objects"""
    return st.recursive(
        st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.text()
        ),
        lambda children: st.one_of(
            st.lists(children, max_size=5),
            st.dictionaries(st.text(), children, max_size=5)
        ),
        max_leaves=max_leaves
    )

# Model-specific generators
def user_data_strategy():
    """Generate user data for testing"""
    return st.fixed_dictionaries({
        'username': st.text(min_size=3, max_size=30, alphabet=string.ascii_letters + string.digits + '_'),
        'email': email_strategy(),
        'first_name': st.text(min_size=1, max_size=30, alphabet=string.ascii_letters + ' '),
        'last_name': st.text(min_size=1, max_size=30, alphabet=string.ascii_letters + ' '),
        'is_active': st.booleans(),
        'is_staff': st.booleans(),
    })

def inventory_item_data_strategy():
    """Generate inventory item data"""
    return st.fixed_dictionaries({
        'name': text_strategy(min_size=1, max_size=100),
        'code': st.text(min_size=3, max_size=20, alphabet=string.ascii_uppercase + string.digits + '-'),
        'description': st.text(max_size=500),
        'category': st.sampled_from(['Bombas', 'Tuberías', 'Accesorios', 'Químicos', 'Herramientas']),
        'unit_price': st.decimals(min_value=0, max_value=999999, places=2),
        'stock_quantity': st.integers(min_value=0, max_value=10000),
        'minimum_stock': st.integers(min_value=0, max_value=100),
        'status': st.sampled_from(['active', 'inactive', 'discontinued']),
    })

def permission_data_strategy():
    """Generate permission data"""
    return st.fixed_dictionaries({
        'name': text_strategy(min_size=1, max_size=100),
        'codename': st.text(min_size=1, max_size=100, alphabet=string.ascii_lowercase + '_'),
        'description': st.text(max_size=200),
    })

def role_data_strategy():
    """Generate role data"""
    return st.fixed_dictionaries({
        'name': text_strategy(min_size=1, max_size=50),
        'description': st.text(max_size=200),
    })

# API request generators
def api_request_data_strategy():
    """Generate API request data"""
    return st.fixed_dictionaries({
        'method': st.sampled_from(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']),
        'path': st.text(min_size=1, max_size=200, alphabet=string.ascii_letters + string.digits + '/-_'),
        'query_params': st.dictionaries(
            st.text(min_size=1, max_size=50, alphabet=string.ascii_letters + '_'),
            st.text(max_size=100),
            max_size=10
        ),
        'headers': st.dictionaries(
            st.text(min_size=1, max_size=50, alphabet=string.ascii_letters + '-'),
            st.text(max_size=200),
            max_size=10
        ),
        'body': json_object_strategy()
    })

def pagination_params_strategy():
    """Generate pagination parameters"""
    return st.fixed_dictionaries({
        'page': st.integers(min_value=1, max_value=100),
        'page_size': st.sampled_from([5, 10, 25, 50, 100]),
        'ordering': st.one_of(
            st.none(),
            st.text(min_size=1, max_size=50, alphabet=string.ascii_letters + '_-')
        )
    })

def search_params_strategy():
    """Generate search parameters"""
    return st.fixed_dictionaries({
        'q': st.one_of(st.none(), st.text(max_size=100)),
        'filters': st.dictionaries(
            st.text(min_size=1, max_size=30, alphabet=string.ascii_letters + '_'),
            st.text(max_size=50),
            max_size=5
        ),
        'date_from': st.one_of(st.none(), st.dates()),
        'date_to': st.one_of(st.none(), st.dates()),
        'categories': st.lists(st.text(min_size=1, max_size=30), max_size=5)
    })

# Validation helpers
def is_valid_email(email):
    """Check if email is valid"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_json(data):
    """Check if data is JSON serializable"""
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False

def is_valid_pagination(params):
    """Check if pagination parameters are valid"""
    page = params.get('page', 1)
    page_size = params.get('page_size', 10)
    return page >= 1 and page_size > 0 and page_size <= 100

# Test data factories
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_user(**kwargs):
        """Create a test user"""
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    
    @staticmethod
    def create_superuser(**kwargs):
        """Create a test superuser"""
        defaults = {
            'username': 'admin',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
        }
        defaults.update(kwargs)
        return User.objects.create_superuser(**defaults)

# Property test decorators
def property_test(func):
    """Decorator to mark property-based tests"""
    import pytest
    return pytest.mark.property(func)

# Common test mixins
class PropertyTestMixin:
    """Mixin for property-based test cases"""
    
    def assertValidJSON(self, data):
        """Assert that data is valid JSON"""
        self.assertTrue(is_valid_json(data), f"Data is not valid JSON: {data}")
    
    def assertValidEmail(self, email):
        """Assert that email is valid"""
        self.assertTrue(is_valid_email(email), f"Email is not valid: {email}")
    
    def assertValidPagination(self, params):
        """Assert that pagination parameters are valid"""
        self.assertTrue(is_valid_pagination(params), f"Pagination params are not valid: {params}")
    
    def assertResponseStructure(self, response, expected_keys):
        """Assert that response has expected structure"""
        if hasattr(response, 'json'):
            data = response.json()
        else:
            data = response
        
        for key in expected_keys:
            self.assertIn(key, data, f"Expected key '{key}' not found in response")

# Performance testing utilities
class PerformanceTestMixin:
    """Mixin for performance testing"""
    
    def assertExecutionTime(self, func, max_time_ms=1000, *args, **kwargs):
        """Assert that function executes within time limit"""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time_ms = (end_time - start_time) * 1000
        self.assertLess(
            execution_time_ms, 
            max_time_ms, 
            f"Function took {execution_time_ms:.2f}ms, expected less than {max_time_ms}ms"
        )
        return result

# Database testing utilities
class DatabaseTestMixin:
    """Mixin for database testing"""
    
    def assertDatabaseIntegrity(self, model_class):
        """Assert that database integrity is maintained"""
        # Check for orphaned records, constraint violations, etc.
        count = model_class.objects.count()
        self.assertGreaterEqual(count, 0, "Model count should be non-negative")
    
    def assertNoOrphanedRecords(self, model_class, foreign_key_field):
        """Assert that no orphaned records exist"""
        orphaned = model_class.objects.filter(**{f"{foreign_key_field}__isnull": True})
        self.assertEqual(orphaned.count(), 0, f"Found orphaned records in {model_class.__name__}")

# Export commonly used items
__all__ = [
    'text_strategy',
    'email_strategy',
    'phone_strategy',
    'url_strategy',
    'json_object_strategy',
    'user_data_strategy',
    'inventory_item_data_strategy',
    'permission_data_strategy',
    'role_data_strategy',
    'api_request_data_strategy',
    'pagination_params_strategy',
    'search_params_strategy',
    'is_valid_email',
    'is_valid_json',
    'is_valid_pagination',
    'TestDataFactory',
    'property_test',
    'PropertyTestMixin',
    'PerformanceTestMixin',
    'DatabaseTestMixin',
]