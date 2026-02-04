"""
Property-based tests for SystemConfiguration model.
Tests universal properties that should hold across all valid inputs.

Feature: system-modernization, Property 31: Configuration Validation
Feature: system-modernization, Property 32: Configuration Profile Support
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.extra.django import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json
import uuid

from inventario.models import SystemConfiguration
from test_utils import PropertyTestMixin, DatabaseTestMixin

User = get_user_model()


# Strategies for generating test data
def valid_config_key_strategy():
    """Generate valid configuration keys in dot notation"""
    parts = st.lists(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz0123456789_',
            min_size=1,
            max_size=20
        ),
        min_size=2,
        max_size=4
    )
    return parts.map(lambda x: '.'.join(x))


def config_value_strategy():
    """Generate various types of configuration values"""
    return st.one_of(
        st.text(min_size=1, max_size=200),  # Ensure non-empty strings
        st.integers(min_value=-1000000, max_value=1000000),
        st.floats(allow_nan=False, allow_infinity=False),
        st.booleans(),
        st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
        st.dictionaries(
            st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=20),
            st.one_of(st.text(min_size=1, max_size=100), st.integers(), st.booleans()),
            min_size=1,
            max_size=5
        )
    )


def environment_strategy():
    """Generate valid environment values"""
    return st.sampled_from([choice[0] for choice in SystemConfiguration.Environment.choices])


def category_strategy():
    """Generate valid category values"""
    return st.sampled_from([choice[0] for choice in SystemConfiguration.Category.choices])


@pytest.mark.property
class SystemConfigurationPropertyTests(TestCase, PropertyTestMixin, DatabaseTestMixin):
    """
    Property-based tests for SystemConfiguration model.
    
    **Validates: Requirements 8.1, 8.2, 8.4**
    """
    
    def setUp(self):
        """Set up test data"""
        # Use unique username for each test
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @given(
        key=valid_config_key_strategy(),
        value=config_value_strategy(),
        environment=environment_strategy(),
        category=category_strategy(),
        description=st.text(max_size=500),
        is_sensitive=st.booleans()
    )
    @settings(max_examples=50)
    def test_configuration_creation_property(self, key, value, environment, category, description, is_sensitive):
        """
        Property: For any valid configuration data, the system should create 
        a configuration successfully and store all provided values correctly.
        
        **Validates: Requirements 8.1**
        """
        # Create configuration
        config = SystemConfiguration.objects.create(
            key=key,
            value=value,
            environment=environment,
            category=category,
            description=description,
            is_sensitive=is_sensitive,
            modified_by=self.user
        )
        
        # Verify all properties are stored correctly
        self.assertEqual(config.key, key)
        self.assertEqual(config.value, value)
        self.assertEqual(config.environment, environment)
        self.assertEqual(config.category, category)
        self.assertEqual(config.description, description)
        self.assertEqual(config.is_sensitive, is_sensitive)
        self.assertEqual(config.modified_by, self.user)
        self.assertTrue(config.is_active)
        self.assertIsNotNone(config.created_at)
        self.assertIsNotNone(config.modified_at)
    
    @given(
        key=valid_config_key_strategy(),
        value=config_value_strategy(),
        environment=environment_strategy()
    )
    @settings(max_examples=30)
    def test_configuration_validation_property(self, key, value, environment):
        """
        Property: For any valid configuration input, the system should validate 
        the configuration successfully without raising validation errors.
        
        **Validates: Requirements 8.2**
        """
        config = SystemConfiguration(
            key=key,
            value=value,
            environment=environment,
            modified_by=self.user
        )
        
        # Should not raise ValidationError for valid inputs
        try:
            config.full_clean()
        except ValidationError:
            self.fail(f"Valid configuration failed validation: key={key}, value={value}, environment={environment}")
    
    @given(
        invalid_key=st.one_of(
            st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=50).filter(lambda x: '.' not in x),
            st.just('')
        ),
        value=config_value_strategy()
    )
    @settings(max_examples=20)
    def test_invalid_key_validation_property(self, invalid_key, value):
        """
        Property: For any invalid configuration key (no dot notation or empty),
        the system should raise a ValidationError during validation.
        
        **Validates: Requirements 8.2**
        """
        assume(invalid_key == '' or '.' not in str(invalid_key))
        
        config = SystemConfiguration(
            key=invalid_key,
            value=value,
            modified_by=self.user
        )
        
        # Should raise ValidationError for invalid keys
        with self.assertRaises(ValidationError) as cm:
            config.full_clean()
        
        # Should specifically mention key validation
        self.assertIn('key', cm.exception.message_dict)
    
    @given(
        key=valid_config_key_strategy(),
        value=config_value_strategy(),
        environments=st.lists(environment_strategy(), min_size=1, max_size=3, unique=True)
    )
    @settings(max_examples=20)
    def test_environment_specific_configuration_property(self, key, value, environments):
        """
        Property: For any configuration key and list of environments, the system 
        should support creating separate configurations for each environment and 
        retrieve the correct value for each environment.
        
        **Validates: Requirements 8.4**
        """
        # Create configurations for different environments
        configs = []
        for i, env in enumerate(environments):
            config_value = f"{value}_{i}" if isinstance(value, str) else value
            config = SystemConfiguration.objects.create(
                key=key,
                value=config_value,
                environment=env,
                modified_by=self.user
            )
            configs.append((config, config_value))
        
        # Verify each environment returns its specific value
        for config, expected_value in configs:
            retrieved_value = SystemConfiguration.get_config(key, environment=config.environment)
            self.assertEqual(retrieved_value, expected_value)
    
    @given(
        key=valid_config_key_strategy(),
        all_env_value=config_value_strategy(),
        specific_env_value=config_value_strategy(),
        specific_environment=environment_strategy().filter(lambda x: x != SystemConfiguration.Environment.ALL),
        query_environment=environment_strategy()
    )
    @settings(max_examples=20)
    def test_environment_fallback_property(self, key, all_env_value, specific_env_value, specific_environment, query_environment):
        """
        Property: For any configuration with both 'all environments' and 
        environment-specific values, querying should return the specific value 
        when available, otherwise fall back to the 'all environments' value.
        
        **Validates: Requirements 8.4**
        """
        assume(all_env_value != specific_env_value)  # Ensure values are different
        
        # Create 'all environments' configuration
        SystemConfiguration.objects.create(
            key=key,
            value=all_env_value,
            environment=SystemConfiguration.Environment.ALL,
            modified_by=self.user
        )
        
        # Create environment-specific configuration
        SystemConfiguration.objects.create(
            key=key,
            value=specific_env_value,
            environment=specific_environment,
            modified_by=self.user
        )
        
        # Query for the specific environment should return specific value
        retrieved_value = SystemConfiguration.get_config(key, environment=specific_environment)
        self.assertEqual(retrieved_value, specific_env_value)
        
        # Query for other environments should return 'all environments' value
        if query_environment != specific_environment:
            retrieved_value = SystemConfiguration.get_config(key, environment=query_environment)
            self.assertEqual(retrieved_value, all_env_value)
    
    @given(
        key=valid_config_key_strategy(),
        initial_value=config_value_strategy(),
        updated_value=config_value_strategy(),
        environment=environment_strategy()
    )
    @settings(max_examples=20)
    def test_configuration_update_property(self, key, initial_value, updated_value, environment):
        """
        Property: For any configuration, updating its value should preserve 
        all other attributes and correctly store the new value.
        
        **Validates: Requirements 8.1, 8.2**
        """
        assume(initial_value != updated_value)  # Ensure values are different
        
        # Create initial configuration
        config = SystemConfiguration.objects.create(
            key=key,
            value=initial_value,
            environment=environment,
            modified_by=self.user
        )
        
        original_id = config.id
        original_created_at = config.created_at
        original_key = config.key
        original_environment = config.environment
        
        # Update the value
        config.value = updated_value
        config.save()
        
        # Verify update
        config.refresh_from_db()
        self.assertEqual(config.id, original_id)  # Same instance
        self.assertEqual(config.key, original_key)  # Key unchanged
        self.assertEqual(config.environment, original_environment)  # Environment unchanged
        self.assertEqual(config.created_at, original_created_at)  # Created timestamp unchanged
        self.assertEqual(config.value, updated_value)  # Value updated
        self.assertGreaterEqual(config.modified_at, original_created_at)  # Modified timestamp updated
    
    @given(
        configurations=st.lists(
            st.tuples(
                valid_config_key_strategy(),
                config_value_strategy(),
                environment_strategy(),
                category_strategy()
            ),
            min_size=1,
            max_size=5,
            unique_by=lambda x: (x[0], x[2])  # Unique by key and environment
        ),
        include_sensitive=st.booleans()
    )
    @settings(max_examples=10)
    def test_export_import_roundtrip_property(self, configurations, include_sensitive):
        """
        Property: For any set of configurations, exporting and then importing 
        should preserve all configuration data without loss or corruption.
        
        **Validates: Requirements 8.6**
        """
        # Create configurations
        created_configs = []
        for key, value, environment, category in configurations:
            config = SystemConfiguration.objects.create(
                key=key,
                value=value,
                environment=environment,
                category=category,
                is_sensitive=include_sensitive,  # Set all to same sensitivity for this test
                modified_by=self.user
            )
            created_configs.append(config)
        
        # Export configurations
        export_data = SystemConfiguration.export_configurations(
            include_sensitive=include_sensitive
        )
        
        # Clear existing configurations
        SystemConfiguration.objects.all().delete()
        
        # Import configurations
        import_results = SystemConfiguration.import_configurations(
            export_data,
            modified_by=self.user
        )
        
        # Verify import results
        self.assertEqual(import_results['created'], len(created_configs))
        self.assertEqual(import_results['updated'], 0)
        self.assertEqual(import_results['skipped'], 0)
        self.assertEqual(len(import_results['errors']), 0)
        
        # Verify all configurations were recreated correctly
        for original_config in created_configs:
            imported_config = SystemConfiguration.objects.get(
                key=original_config.key,
                environment=original_config.environment
            )
            
            self.assertEqual(imported_config.value, original_config.value)
            self.assertEqual(imported_config.category, original_config.category)
            self.assertEqual(imported_config.is_sensitive, original_config.is_sensitive)
    
    @given(
        key=valid_config_key_strategy(),
        value=config_value_strategy(),
        category=category_strategy(),
        environment=environment_strategy()
    )
    @settings(max_examples=20)
    def test_get_set_config_consistency_property(self, key, value, category, environment):
        """
        Property: For any configuration key and value, setting a configuration 
        and then getting it should return the exact same value.
        
        **Validates: Requirements 8.1**
        """
        # Set configuration
        SystemConfiguration.set_config(
            key=key,
            value=value,
            category=category,
            environment=environment,
            modified_by=self.user
        )
        
        # Get configuration
        retrieved_value = SystemConfiguration.get_config(key, environment=environment)
        
        # Should be exactly the same
        self.assertEqual(retrieved_value, value)
    
    @given(
        key=valid_config_key_strategy(),
        values=st.lists(config_value_strategy(), min_size=2, max_size=3),
        environment=environment_strategy()
    )
    @settings(max_examples=15)
    def test_configuration_overwrite_property(self, key, values, environment):
        """
        Property: For any configuration key, setting multiple values in sequence 
        should result in only the last value being stored and retrieved.
        
        **Validates: Requirements 8.1, 8.2**
        """
        # Set multiple values in sequence
        for value in values:
            SystemConfiguration.set_config(
                key=key,
                value=value,
                environment=environment,
                modified_by=self.user
            )
        
        # Should only have one configuration for this key/environment
        configs = SystemConfiguration.objects.filter(key=key, environment=environment)
        self.assertEqual(configs.count(), 1)
        
        # Should have the last value
        retrieved_value = SystemConfiguration.get_config(key, environment=environment)
        self.assertEqual(retrieved_value, values[-1])
    
    @given(
        category=category_strategy(),
        configs=st.lists(
            st.tuples(
                valid_config_key_strategy(),
                config_value_strategy(),
                environment_strategy()
            ),
            min_size=1,
            max_size=5,
            unique_by=lambda x: (x[0], x[2])  # Unique by key and environment
        )
    )
    @settings(max_examples=10)
    def test_category_filtering_property(self, category, configs):
        """
        Property: For any category and set of configurations, filtering by 
        category should return only configurations belonging to that category.
        
        **Validates: Requirements 8.1**
        """
        # Create configurations with the specified category
        category_configs = []
        for key, value, environment in configs:
            config = SystemConfiguration.objects.create(
                key=key,
                value=value,
                environment=environment,
                category=category,
                modified_by=self.user
            )
            category_configs.append(config)
        
        # Create some configurations with different categories
        other_categories = [cat for cat in SystemConfiguration.Category.choices if cat[0] != category]
        if other_categories:
            other_category = other_categories[0][0]
            SystemConfiguration.objects.create(
                key='other.config',
                value='other_value',
                category=other_category,
                modified_by=self.user
            )
        
        # Get configurations by category
        filtered_configs = SystemConfiguration.get_by_category(category)
        
        # Should return exactly the configurations we created for this category
        self.assertEqual(filtered_configs.count(), len(category_configs))
        
        # All returned configurations should have the correct category
        for config in filtered_configs:
            self.assertEqual(config.category, category)


@pytest.mark.property
class SystemConfigurationValidationPropertyTests(TestCase, PropertyTestMixin, DatabaseTestMixin):
    """
    Property-based tests specifically for configuration validation.
    
    **Validates: Requirements 8.2**
    """
    
    def setUp(self):
        """Set up test data"""
        # Use unique username for each test
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @given(
        key=valid_config_key_strategy(),
        value=config_value_strategy()
    )
    @settings(max_examples=30)
    def test_valid_configuration_never_fails_validation(self, key, value):
        """
        Property: Any configuration with a valid key format should pass validation,
        regardless of the value type or content.
        
        **Validates: Requirements 8.2**
        """
        config = SystemConfiguration(
            key=key,
            value=value,
            modified_by=self.user
        )
        
        # Should never raise ValidationError for valid key format
        try:
            config.full_clean()
        except ValidationError as e:
            # If validation fails, it should not be due to key format
            if 'key' in e.message_dict:
                self.fail(f"Valid key format failed validation: {key}")
    
    @given(
        key=valid_config_key_strategy(),
        value=config_value_strategy(),
        environment1=environment_strategy(),
        environment2=environment_strategy()
    )
    @settings(max_examples=20)
    def test_unique_constraint_enforcement_property(self, key, value, environment1, environment2):
        """
        Property: For any key and environment combination, only one configuration 
        should be allowed. Attempting to create duplicates should fail.
        
        **Validates: Requirements 8.2**
        """
        # Create first configuration
        SystemConfiguration.objects.create(
            key=key,
            value=value,
            environment=environment1,
            modified_by=self.user
        )
        
        if environment1 == environment2:
            # Same environment - should fail
            with self.assertRaises(Exception):  # IntegrityError or ValidationError
                SystemConfiguration.objects.create(
                    key=key,
                    value=value,
                    environment=environment2,
                    modified_by=self.user
                )
        else:
            # Different environment - should succeed
            config2 = SystemConfiguration.objects.create(
                key=key,
                value=value,
                environment=environment2,
                modified_by=self.user
            )
            self.assertIsNotNone(config2.id)