"""
Setup Test for Backend Property-Based Testing
Verifies that Hypothesis and Django testing environment work correctly
"""

import pytest
from hypothesis import given, strategies as st
from django.test import TestCase
from django.contrib.auth import get_user_model
from test_utils import (
    user_data_strategy, 
    email_strategy, 
    text_strategy,
    PropertyTestMixin
)

User = get_user_model()


class SetupTestCase(TestCase, PropertyTestMixin):
    """Test case to verify testing setup"""
    
    def test_django_setup(self):
        """Test that Django testing environment works"""
        self.assertTrue(True)
        
    def test_hypothesis_basic(self):
        """Test that Hypothesis works with basic strategies"""
        @given(st.text())
        def test_text_property(text):
            self.assertIsInstance(text, str)
        
        test_text_property()
    
    def test_custom_strategies(self):
        """Test that custom strategies work"""
        @given(email_strategy())
        def test_email_property(email):
            self.assertValidEmail(email)
        
        test_email_property()
    
    def test_user_data_strategy(self):
        """Test user data generation strategy"""
        @given(user_data_strategy())
        def test_user_data_property(user_data):
            # Verify required fields are present
            self.assertIn('username', user_data)
            self.assertIn('email', user_data)
            self.assertIn('first_name', user_data)
            self.assertIn('last_name', user_data)
            
            # Verify data types
            self.assertIsInstance(user_data['username'], str)
            self.assertIsInstance(user_data['email'], str)
            self.assertIsInstance(user_data['is_active'], bool)
            self.assertIsInstance(user_data['is_staff'], bool)
            
            # Verify email format
            self.assertValidEmail(user_data['email'])
        
        test_user_data_property()


@pytest.mark.property
class TestPropertyBasedSetup:
    """Pytest-style property-based tests"""
    
    @given(st.text(min_size=1, max_size=100))
    def test_text_generation(self, text):
        """Test text generation with Hypothesis"""
        assert isinstance(text, str)
        assert len(text) >= 1
        assert len(text) <= 100
    
    @given(st.integers(min_value=0, max_value=1000))
    def test_integer_generation(self, number):
        """Test integer generation with Hypothesis"""
        assert isinstance(number, int)
        assert 0 <= number <= 1000
    
    @given(st.lists(st.text(), min_size=0, max_size=10))
    def test_list_generation(self, text_list):
        """Test list generation with Hypothesis"""
        assert isinstance(text_list, list)
        assert len(text_list) <= 10
        for item in text_list:
            assert isinstance(item, str)


def test_hypothesis_integration():
    """Test that Hypothesis integrates with pytest"""
    @given(st.text())
    def property_test(text):
        assert isinstance(text, str)
    
    property_test()


def test_django_models_available():
    """Test that Django models are available"""
    assert User is not None
    assert hasattr(User, 'objects')


if __name__ == '__main__':
    pytest.main([__file__])