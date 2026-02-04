"""
Unit tests for SystemConfiguration model.
Tests the system configuration management functionality.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json

from inventario.models import SystemConfiguration

User = get_user_model()


class SystemConfigurationModelTests(TestCase):
    """Unit tests for SystemConfiguration model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_basic_configuration(self):
        """Test creating a basic system configuration"""
        config = SystemConfiguration.objects.create(
            key='email.smtp_host',
            value='smtp.example.com',
            description='SMTP server hostname',
            category=SystemConfiguration.Category.EMAIL,
            modified_by=self.user
        )
        
        self.assertEqual(config.key, 'email.smtp_host')
        self.assertEqual(config.value, 'smtp.example.com')
        self.assertEqual(config.category, SystemConfiguration.Category.EMAIL)
        self.assertEqual(config.environment, SystemConfiguration.Environment.ALL)
        self.assertFalse(config.is_sensitive)
        self.assertTrue(config.is_active)
        self.assertEqual(config.modified_by, self.user)
    
    def test_environment_specific_configuration(self):
        """Test creating environment-specific configurations"""
        # Production config
        prod_config = SystemConfiguration.objects.create(
            key='database.max_connections',
            value=100,
            environment=SystemConfiguration.Environment.PRODUCTION,
            category=SystemConfiguration.Category.PERFORMANCE,
            modified_by=self.user
        )
        
        # Development config
        dev_config = SystemConfiguration.objects.create(
            key='database.max_connections',
            value=10,
            environment=SystemConfiguration.Environment.DEVELOPMENT,
            category=SystemConfiguration.Category.PERFORMANCE,
            modified_by=self.user
        )
        
        self.assertEqual(prod_config.value, 100)
        self.assertEqual(dev_config.value, 10)
        self.assertEqual(prod_config.key, dev_config.key)
        self.assertNotEqual(prod_config.environment, dev_config.environment)
    
    def test_sensitive_configuration(self):
        """Test creating sensitive configurations"""
        config = SystemConfiguration.objects.create(
            key='email.smtp_password',
            value='secret123',
            category=SystemConfiguration.Category.EMAIL,
            is_sensitive=True,
            modified_by=self.user
        )
        
        self.assertTrue(config.is_sensitive)
        self.assertEqual(config.value, 'secret123')
    
    def test_json_value_storage(self):
        """Test storing complex JSON values"""
        complex_value = {
            'servers': ['server1.com', 'server2.com'],
            'timeout': 30,
            'retry_count': 3,
            'options': {
                'ssl': True,
                'port': 587
            }
        }
        
        config = SystemConfiguration.objects.create(
            key='email.smtp_config',
            value=complex_value,
            category=SystemConfiguration.Category.EMAIL,
            modified_by=self.user
        )
        
        self.assertEqual(config.value, complex_value)
        self.assertIsInstance(config.value, dict)
        self.assertEqual(config.value['servers'], ['server1.com', 'server2.com'])
        self.assertEqual(config.value['options']['ssl'], True)
    
    def test_key_validation(self):
        """Test configuration key validation"""
        # Valid key
        config = SystemConfiguration(
            key='email.smtp_host',
            value='smtp.example.com',
            modified_by=self.user
        )
        config.full_clean()  # Should not raise
        
        # Invalid key - no dot notation
        config_invalid = SystemConfiguration(
            key='invalidkey',
            value='some_value',
            modified_by=self.user
        )
        
        with self.assertRaises(ValidationError) as cm:
            config_invalid.full_clean()
        
        self.assertIn('key', cm.exception.message_dict)
        self.assertIn('dot notation', cm.exception.message_dict['key'][0])
    
    def test_unique_together_constraint(self):
        """Test unique_together constraint on key and environment"""
        # Create first config
        SystemConfiguration.objects.create(
            key='test.setting',
            value='value1',
            environment=SystemConfiguration.Environment.PRODUCTION,
            modified_by=self.user
        )
        
        # Try to create duplicate - should fail
        with self.assertRaises(Exception):  # IntegrityError
            SystemConfiguration.objects.create(
                key='test.setting',
                value='value2',
                environment=SystemConfiguration.Environment.PRODUCTION,
                modified_by=self.user
            )
    
    def test_get_config_method(self):
        """Test the get_config class method"""
        # Create configurations
        SystemConfiguration.objects.create(
            key='test.setting',
            value='all_env_value',
            environment=SystemConfiguration.Environment.ALL,
            modified_by=self.user
        )
        
        SystemConfiguration.objects.create(
            key='test.setting',
            value='prod_value',
            environment=SystemConfiguration.Environment.PRODUCTION,
            modified_by=self.user
        )
        
        # Test getting environment-specific value
        value = SystemConfiguration.get_config(
            'test.setting', 
            environment=SystemConfiguration.Environment.PRODUCTION
        )
        self.assertEqual(value, 'prod_value')
        
        # Test fallback to 'all environments'
        value = SystemConfiguration.get_config(
            'test.setting', 
            environment=SystemConfiguration.Environment.DEVELOPMENT
        )
        self.assertEqual(value, 'all_env_value')
        
        # Test default value
        value = SystemConfiguration.get_config(
            'nonexistent.setting',
            default='default_value'
        )
        self.assertEqual(value, 'default_value')
    
    def test_set_config_method(self):
        """Test the set_config class method"""
        # Set new configuration
        config = SystemConfiguration.set_config(
            key='new.setting',
            value='new_value',
            category=SystemConfiguration.Category.GENERAL,
            description='Test setting',
            modified_by=self.user
        )
        
        self.assertEqual(config.key, 'new.setting')
        self.assertEqual(config.value, 'new_value')
        self.assertEqual(config.category, SystemConfiguration.Category.GENERAL)
        
        # Update existing configuration
        updated_config = SystemConfiguration.set_config(
            key='new.setting',
            value='updated_value',
            modified_by=self.user
        )
        
        self.assertEqual(updated_config.pk, config.pk)
        self.assertEqual(updated_config.value, 'updated_value')
    
    def test_get_by_category_method(self):
        """Test the get_by_category class method"""
        # Create configurations in different categories
        SystemConfiguration.objects.create(
            key='email.host',
            value='smtp.example.com',
            category=SystemConfiguration.Category.EMAIL,
            modified_by=self.user
        )
        
        SystemConfiguration.objects.create(
            key='email.port',
            value=587,
            category=SystemConfiguration.Category.EMAIL,
            modified_by=self.user
        )
        
        SystemConfiguration.objects.create(
            key='security.max_attempts',
            value=5,
            category=SystemConfiguration.Category.SECURITY,
            modified_by=self.user
        )
        
        # Get email configurations
        email_configs = SystemConfiguration.get_by_category(
            SystemConfiguration.Category.EMAIL
        )
        
        self.assertEqual(email_configs.count(), 2)
        keys = [config.key for config in email_configs]
        self.assertIn('email.host', keys)
        self.assertIn('email.port', keys)
        self.assertNotIn('security.max_attempts', keys)
    
    def test_export_configurations(self):
        """Test configuration export functionality"""
        # Create test configurations
        SystemConfiguration.objects.create(
            key='test.setting1',
            value='value1',
            category=SystemConfiguration.Category.GENERAL,
            environment=SystemConfiguration.Environment.PRODUCTION,
            modified_by=self.user
        )
        
        SystemConfiguration.objects.create(
            key='test.setting2',
            value='value2',
            category=SystemConfiguration.Category.GENERAL,
            is_sensitive=True,
            modified_by=self.user
        )
        
        # Export without sensitive data
        export_data = SystemConfiguration.export_configurations(
            include_sensitive=False
        )
        
        self.assertIn('export_timestamp', export_data)
        self.assertIn('configurations', export_data)
        self.assertEqual(len(export_data['configurations']), 1)
        self.assertEqual(export_data['configurations'][0]['key'], 'test.setting1')
        
        # Export with sensitive data
        export_data_sensitive = SystemConfiguration.export_configurations(
            include_sensitive=True
        )
        
        self.assertEqual(len(export_data_sensitive['configurations']), 2)
    
    def test_import_configurations(self):
        """Test configuration import functionality"""
        import_data = {
            'configurations': [
                {
                    'key': 'imported.setting1',
                    'value': 'imported_value1',
                    'category': 'general',
                    'environment': 'all',
                    'is_sensitive': False,
                    'description': 'Imported setting 1'
                },
                {
                    'key': 'imported.setting2',
                    'value': 'imported_value2',
                    'category': 'security',
                    'environment': 'production',
                    'is_sensitive': True,
                    'description': 'Imported setting 2'
                }
            ]
        }
        
        # Import configurations
        results = SystemConfiguration.import_configurations(
            import_data, 
            modified_by=self.user
        )
        
        self.assertEqual(results['created'], 2)
        self.assertEqual(results['updated'], 0)
        self.assertEqual(results['skipped'], 0)
        self.assertEqual(len(results['errors']), 0)
        
        # Verify configurations were created
        config1 = SystemConfiguration.objects.get(key='imported.setting1')
        self.assertEqual(config1.value, 'imported_value1')
        self.assertEqual(config1.category, SystemConfiguration.Category.GENERAL)
        
        config2 = SystemConfiguration.objects.get(key='imported.setting2')
        self.assertEqual(config2.value, 'imported_value2')
        self.assertTrue(config2.is_sensitive)
    
    def test_string_representation(self):
        """Test string representation of configurations"""
        # Configuration for all environments
        config_all = SystemConfiguration.objects.create(
            key='test.setting',
            value='value',
            environment=SystemConfiguration.Environment.ALL,
            modified_by=self.user
        )
        
        self.assertEqual(str(config_all), 'test.setting')
        
        # Environment-specific configuration
        config_prod = SystemConfiguration.objects.create(
            key='test.setting2',
            value='value',
            environment=SystemConfiguration.Environment.PRODUCTION,
            modified_by=self.user
        )
        
        self.assertEqual(str(config_prod), 'test.setting2 (production)')
    
    def test_inactive_configurations(self):
        """Test that inactive configurations are not returned by get_config"""
        # Create active configuration
        SystemConfiguration.objects.create(
            key='test.active',
            value='active_value',
            is_active=True,
            modified_by=self.user
        )
        
        # Create inactive configuration
        SystemConfiguration.objects.create(
            key='test.inactive',
            value='inactive_value',
            is_active=False,
            modified_by=self.user
        )
        
        # Active config should be found
        value = SystemConfiguration.get_config('test.active')
        self.assertEqual(value, 'active_value')
        
        # Inactive config should not be found
        value = SystemConfiguration.get_config('test.inactive', default='default')
        self.assertEqual(value, 'default')


class SystemConfigurationIntegrationTests(TestCase):
    """Integration tests for SystemConfiguration with other models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_audit_trail_integration(self):
        """Test that configuration changes create audit trail entries"""
        # Create configuration
        config = SystemConfiguration.objects.create(
            key='test.audit',
            value='initial_value',
            modified_by=self.user
        )
        
        # Update configuration
        config.value = 'updated_value'
        config.save()
        
        # Check that audit trail was created (if auditoria app is available)
        try:
            from auditoria.models import AuditLog
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(SystemConfiguration)
            audit_entries = AuditLog.objects.filter(
                content_type=content_type,
                object_id=config.pk
            )
            
            # Should have at least one audit entry
            self.assertGreater(audit_entries.count(), 0)
            
        except ImportError:
            # AuditLog not available, skip this test
            pass
    
    def test_user_relationship(self):
        """Test relationship with User model"""
        config = SystemConfiguration.objects.create(
            key='test.user_relation',
            value='test_value',
            modified_by=self.user
        )
        
        self.assertEqual(config.modified_by, self.user)
        
        # Test that deleting user sets modified_by to null
        user_id = self.user.id
        self.user.delete()
        
        config.refresh_from_db()
        self.assertIsNone(config.modified_by)