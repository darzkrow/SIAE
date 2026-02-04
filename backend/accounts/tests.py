"""
Tests for the dynamic permission system models.
Includes both unit tests and property-based tests.
"""

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import from_model
import pytest
from datetime import timedelta

from accounts.models import Permission, Role, RolePermission, UserRole
from test_utils import (
    permission_data_strategy,
    role_data_strategy,
    PropertyTestMixin,
    DatabaseTestMixin,
    TestDataFactory
)

User = get_user_model()


class PermissionModelTests(TestCase, PropertyTestMixin, DatabaseTestMixin):
    """Unit tests for Permission model"""
    
    def setUp(self):
        self.content_type = ContentType.objects.get_for_model(User)
    
    def test_permission_creation(self):
        """Test basic permission creation"""
        permission = Permission.objects.create(
            name="Can view users",
            codename="view_user",
            content_type=self.content_type,
            description="Allows viewing user details"
        )
        
        self.assertEqual(permission.name, "Can view users")
        self.assertEqual(permission.codename, "view_user")
        self.assertEqual(permission.content_type, self.content_type)
        self.assertTrue(permission.created_at)
        self.assertTrue(permission.updated_at)
    
    def test_permission_str_representation(self):
        """Test permission string representation"""
        permission = Permission.objects.create(
            name="Can edit users",
            codename="edit_user",
            content_type=self.content_type
        )
        
        expected = f"{self.content_type.app_label}.edit_user"
        self.assertEqual(str(permission), expected)
    
    def test_permission_unique_constraint(self):
        """Test that content_type + codename must be unique"""
        Permission.objects.create(
            name="Can view users",
            codename="view_user",
            content_type=self.content_type
        )
        
        with self.assertRaises(IntegrityError):
            Permission.objects.create(
                name="Can view users again",
                codename="view_user",
                content_type=self.content_type
            )
    
    def test_permission_ordering(self):
        """Test permission ordering"""
        user_ct = ContentType.objects.get_for_model(User)
        role_ct = ContentType.objects.get_for_model(Role)
        
        perm1 = Permission.objects.create(
            name="View Role", codename="view_role", content_type=role_ct
        )
        perm2 = Permission.objects.create(
            name="View User", codename="view_user", content_type=user_ct
        )
        
        permissions = list(Permission.objects.all())
        # Should be ordered by app_label, model, codename
        self.assertTrue(permissions.index(perm2) < permissions.index(perm1))


class RoleModelTests(TestCase, PropertyTestMixin, DatabaseTestMixin):
    """Unit tests for Role model"""
    
    def test_role_creation(self):
        """Test basic role creation"""
        role = Role.objects.create(
            name="Administrator",
            description="Full system access"
        )
        
        self.assertEqual(role.name, "Administrator")
        self.assertEqual(role.description, "Full system access")
        self.assertTrue(role.is_active)
        self.assertTrue(role.created_at)
        self.assertTrue(role.updated_at)
    
    def test_role_str_representation(self):
        """Test role string representation"""
        role = Role.objects.create(name="Manager")
        self.assertEqual(str(role), "Manager")
    
    def test_role_unique_name(self):
        """Test that role names must be unique"""
        Role.objects.create(name="Administrator")
        
        with self.assertRaises(IntegrityError):
            Role.objects.create(name="Administrator")


class RolePermissionModelTests(TestCase, PropertyTestMixin, DatabaseTestMixin):
    """Unit tests for RolePermission through model"""
    
    def setUp(self):
        self.content_type = ContentType.objects.get_for_model(User)
        self.role = Role.objects.create(name="Test Role")
        self.permission = Permission.objects.create(
            name="Test Permission",
            codename="test_perm",
            content_type=self.content_type
        )
    
    def test_role_permission_creation(self):
        """Test basic role-permission relationship creation"""
        role_perm = RolePermission.objects.create(
            role=self.role,
            permission=self.permission,
            granted=True,
            conditions={"department": "IT"}
        )
        
        self.assertEqual(role_perm.role, self.role)
        self.assertEqual(role_perm.permission, self.permission)
        self.assertTrue(role_perm.granted)
        self.assertEqual(role_perm.conditions, {"department": "IT"})
        self.assertTrue(role_perm.created_at)
    
    def test_role_permission_str_representation(self):
        """Test role-permission string representation"""
        role_perm = RolePermission.objects.create(
            role=self.role,
            permission=self.permission,
            granted=True
        )
        
        expected = f"{self.role.name} - {self.permission.codename} (granted)"
        self.assertEqual(str(role_perm), expected)
    
    def test_role_permission_denied(self):
        """Test denied permission representation"""
        role_perm = RolePermission.objects.create(
            role=self.role,
            permission=self.permission,
            granted=False
        )
        
        expected = f"{self.role.name} - {self.permission.codename} (denied)"
        self.assertEqual(str(role_perm), expected)
    
    def test_role_permission_unique_constraint(self):
        """Test that role-permission combination must be unique"""
        RolePermission.objects.create(
            role=self.role,
            permission=self.permission
        )
        
        with self.assertRaises(IntegrityError):
            RolePermission.objects.create(
                role=self.role,
                permission=self.permission
            )


class UserRoleModelTests(TestCase, PropertyTestMixin, DatabaseTestMixin):
    """Unit tests for UserRole through model"""
    
    def setUp(self):
        self.user = TestDataFactory.create_user(username="testuser")
        self.assigner = TestDataFactory.create_user(username="admin")
        self.role = Role.objects.create(name="Test Role")
    
    def test_user_role_creation(self):
        """Test basic user-role relationship creation"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.assigner
        )
        
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertEqual(user_role.assigned_by, self.assigner)
        self.assertTrue(user_role.is_active)
        self.assertTrue(user_role.assigned_at)
        self.assertIsNone(user_role.expires_at)
    
    def test_user_role_str_representation(self):
        """Test user-role string representation"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role
        )
        
        expected = f"{self.user.username} - {self.role.name}"
        self.assertEqual(str(user_role), expected)
    
    def test_user_role_expiration(self):
        """Test role expiration functionality"""
        future_date = timezone.now() + timedelta(days=30)
        past_date = timezone.now() - timedelta(days=1)
        
        # Non-expiring role
        user_role1 = UserRole.objects.create(
            user=self.user,
            role=self.role
        )
        self.assertFalse(user_role1.is_expired)
        
        # Future expiration
        user_role2 = UserRole.objects.create(
            user=self.user,
            role=Role.objects.create(name="Future Role"),
            expires_at=future_date
        )
        self.assertFalse(user_role2.is_expired)
        
        # Past expiration
        user_role3 = UserRole.objects.create(
            user=self.user,
            role=Role.objects.create(name="Expired Role"),
            expires_at=past_date
        )
        self.assertTrue(user_role3.is_expired)
    
    def test_user_role_unique_constraint(self):
        """Test that user-role combination must be unique"""
        UserRole.objects.create(user=self.user, role=self.role)
        
        with self.assertRaises(IntegrityError):
            UserRole.objects.create(user=self.user, role=self.role)


class CustomUserModelTests(TestCase, PropertyTestMixin, DatabaseTestMixin):
    """Unit tests for CustomUser model extensions"""
    
    def setUp(self):
        self.user = TestDataFactory.create_user(username="testuser")
        self.content_type = ContentType.objects.get_for_model(User)
        
        # Create test permissions
        self.view_perm = Permission.objects.create(
            name="Can view users",
            codename="view_user",
            content_type=self.content_type
        )
        self.edit_perm = Permission.objects.create(
            name="Can edit users",
            codename="edit_user",
            content_type=self.content_type
        )
        
        # Create test role with permissions
        self.role = Role.objects.create(name="Editor")
        RolePermission.objects.create(
            role=self.role,
            permission=self.view_perm,
            granted=True
        )
        RolePermission.objects.create(
            role=self.role,
            permission=self.edit_perm,
            granted=True
        )
    
    def test_get_dynamic_permissions(self):
        """Test getting permissions from assigned roles"""
        # Assign role to user
        UserRole.objects.create(user=self.user, role=self.role)
        
        permissions = self.user.get_dynamic_permissions()
        self.assertEqual(permissions.count(), 2)
        self.assertIn(self.view_perm, permissions)
        self.assertIn(self.edit_perm, permissions)
    
    def test_get_dynamic_permissions_inactive_role(self):
        """Test that inactive roles don't grant permissions"""
        # Make role inactive
        self.role.is_active = False
        self.role.save()
        
        UserRole.objects.create(user=self.user, role=self.role)
        
        permissions = self.user.get_dynamic_permissions()
        self.assertEqual(permissions.count(), 0)
    
    def test_get_dynamic_permissions_expired_assignment(self):
        """Test that expired role assignments don't grant permissions"""
        past_date = timezone.now() - timedelta(days=1)
        
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            expires_at=past_date
        )
        
        permissions = self.user.get_dynamic_permissions()
        self.assertEqual(permissions.count(), 0)
    
    def test_get_dynamic_permissions_denied_permission(self):
        """Test that denied permissions are not included"""
        # Create a denied permission
        denied_perm = Permission.objects.create(
            name="Can delete users",
            codename="delete_user",
            content_type=self.content_type
        )
        RolePermission.objects.create(
            role=self.role,
            permission=denied_perm,
            granted=False
        )
        
        UserRole.objects.create(user=self.user, role=self.role)
        
        permissions = self.user.get_dynamic_permissions()
        self.assertEqual(permissions.count(), 2)  # Only granted permissions
        self.assertNotIn(denied_perm, permissions)
    
    def test_has_dynamic_permission(self):
        """Test checking for specific permissions"""
        UserRole.objects.create(user=self.user, role=self.role)
        
        self.assertTrue(self.user.has_dynamic_permission("view_user"))
        self.assertTrue(self.user.has_dynamic_permission("edit_user"))
        self.assertFalse(self.user.has_dynamic_permission("delete_user"))
    
    def test_has_dynamic_permission_with_content_type(self):
        """Test checking permissions with content type filter"""
        UserRole.objects.create(user=self.user, role=self.role)
        
        self.assertTrue(
            self.user.has_dynamic_permission("view_user", self.content_type)
        )
        
        # Different content type should return False
        role_ct = ContentType.objects.get_for_model(Role)
        self.assertFalse(
            self.user.has_dynamic_permission("view_user", role_ct)
        )


# Property-Based Tests
from hypothesis.extra.django import TestCase as HypothesisTestCase

class PermissionPropertyTests(HypothesisTestCase, PropertyTestMixin):
    """Property-based tests for Permission model"""
    
    @given(permission_data_strategy())
    @settings(max_examples=50)
    def test_permission_creation_property(self, permission_data):
        """Property: Any valid permission data should create a valid permission"""
        content_type = ContentType.objects.get_for_model(User)
        
        permission = Permission.objects.create(
            name=permission_data['name'],
            codename=permission_data['codename'],
            content_type=content_type,
            description=permission_data['description']
        )
        
        # Verify the permission was created correctly
        self.assertEqual(permission.name, permission_data['name'])
        self.assertEqual(permission.codename, permission_data['codename'])
        self.assertEqual(permission.content_type, content_type)
        self.assertEqual(permission.description, permission_data['description'])
        self.assertIsNotNone(permission.created_at)
        self.assertIsNotNone(permission.updated_at)
        
        # Verify string representation
        expected_str = f"{content_type.app_label}.{permission_data['codename']}"
        self.assertEqual(str(permission), expected_str)


class RolePropertyTests(HypothesisTestCase, PropertyTestMixin):
    """Property-based tests for Role model"""
    
    @given(role_data_strategy())
    @settings(max_examples=50)
    def test_role_creation_property(self, role_data):
        """Property: Any valid role data should create a valid role"""
        role = Role.objects.create(
            name=role_data['name'],
            description=role_data['description']
        )
        
        # Verify the role was created correctly
        self.assertEqual(role.name, role_data['name'])
        self.assertEqual(role.description, role_data['description'])
        self.assertTrue(role.is_active)  # Default value
        self.assertIsNotNone(role.created_at)
        self.assertIsNotNone(role.updated_at)
        
        # Verify string representation
        self.assertEqual(str(role), role_data['name'])


class PermissionSystemIntegrationTests(TestCase, PropertyTestMixin):
    """Integration tests for the complete permission system"""
    
    def test_complete_permission_workflow(self):
        """Test a complete permission assignment and checking workflow"""
        # Create users
        admin = TestDataFactory.create_superuser(username="admin")
        user = TestDataFactory.create_user(username="testuser")
        
        # Create content type and permissions
        content_type = ContentType.objects.get_for_model(User)
        view_perm = Permission.objects.create(
            name="Can view users",
            codename="view_user",
            content_type=content_type
        )
        edit_perm = Permission.objects.create(
            name="Can edit users",
            codename="edit_user",
            content_type=content_type
        )
        
        # Create role and assign permissions
        role = Role.objects.create(name="User Manager")
        RolePermission.objects.create(role=role, permission=view_perm, granted=True)
        RolePermission.objects.create(role=role, permission=edit_perm, granted=True)
        
        # Assign role to user
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=admin
        )
        
        # Test permission checking
        self.assertTrue(user.has_dynamic_permission("view_user"))
        self.assertTrue(user.has_dynamic_permission("edit_user"))
        self.assertFalse(user.has_dynamic_permission("delete_user"))
        
        # Test permission retrieval
        permissions = user.get_dynamic_permissions()
        self.assertEqual(permissions.count(), 2)
        
        # Test role deactivation
        role.is_active = False
        role.save()
        
        permissions = user.get_dynamic_permissions()
        self.assertEqual(permissions.count(), 0)
        
        # Test role expiration
        role.is_active = True
        role.save()
        user_role.expires_at = timezone.now() - timedelta(days=1)
        user_role.save()
        
        permissions = user.get_dynamic_permissions()
        self.assertEqual(permissions.count(), 0)


# Mark property tests
pytest.mark.property = pytest.mark.property if hasattr(pytest.mark, 'property') else lambda x: x