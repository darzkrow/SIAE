"""
Property-based test for Permission Storage Integrity
**Feature: system-modernization, Property 12: Permission Storage Integrity**
**Validates: Requirements 3.1**

This test validates that permission data is stored correctly in database tables
and maintains referential integrity across all permission-related operations.
"""

import pytest
from django.test import TestCase, TransactionTestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from datetime import timedelta
import json
import uuid

from accounts.models import Permission, Role, RolePermission, UserRole
from test_utils import (
    permission_data_strategy,
    role_data_strategy,
    json_object_strategy,
    PropertyTestMixin,
    DatabaseTestMixin,
    TestDataFactory
)

User = get_user_model()


@pytest.mark.property
class PermissionStorageIntegrityPropertyTest(HypothesisTestCase, PropertyTestMixin, DatabaseTestMixin):
    """
    Property-based test for permission storage integrity.
    
    **Property 12: Permission Storage Integrity**
    **Validates: Requirements 3.1**
    
    Tests that any permission or role data stored in the database maintains
    proper structure, relationships, and referential integrity across all
    permission-related operations.
    """
    
    def setUp(self):
        """Set up test data"""
        self.content_types = [
            ContentType.objects.get_for_model(User),
            ContentType.objects.get_for_model(Role),
            ContentType.objects.get_for_model(Permission),
        ]
        # Create unique admin user for each test
        unique_id = str(uuid.uuid4())[:8]
        self.admin_user = TestDataFactory.create_superuser(username=f"test_admin_{unique_id}")
    
    @given(permission_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_permission_storage_integrity(self, permission_data):
        """
        Property: Any valid permission data should be stored correctly
        with proper referential integrity.
        """
        # Assume valid data constraints
        assume(len(permission_data['name'].strip()) > 0)
        assume(len(permission_data['codename'].strip()) > 0)
        assume(permission_data['codename'].replace('_', '').replace('-', '').isalnum())
        
        # Use data() to draw content type instead of example()
        content_type = self.content_types[0]  # Use first content type for simplicity
        
        # Make codename unique to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        unique_codename = f"{permission_data['codename'].strip().lower()}_{unique_id}"
        
        # Create permission
        permission = Permission.objects.create(
            name=permission_data['name'].strip(),
            codename=unique_codename,
            content_type=content_type,
            description=permission_data['description']
        )
        
        # Verify storage integrity
        self._verify_permission_storage_integrity(permission, permission_data, content_type, unique_codename)
        
        # Verify database constraints
        self._verify_permission_database_constraints(permission)
        
        # Verify referential integrity
        self._verify_permission_referential_integrity(permission)
    
    @given(role_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_role_storage_integrity(self, role_data):
        """
        Property: Any valid role data should be stored correctly
        with proper referential integrity.
        """
        # Assume valid data constraints
        assume(len(role_data['name'].strip()) > 0)
        
        # Create role
        role = Role.objects.create(
            name=role_data['name'].strip(),
            description=role_data['description']
        )
        
        # Verify storage integrity
        self._verify_role_storage_integrity(role, role_data)
        
        # Verify database constraints
        self._verify_role_database_constraints(role)
        
        # Verify referential integrity
        self._verify_role_referential_integrity(role)
    
    @given(
        permission_data_strategy(),
        role_data_strategy(),
        st.booleans(),
        st.one_of(st.none(), json_object_strategy(max_leaves=5))
    )
    @settings(max_examples=100, deadline=None)
    def test_role_permission_relationship_integrity(self, permission_data, role_data, granted, conditions):
        """
        Property: Any valid role-permission relationship should maintain
        referential integrity and store conditions correctly.
        """
        # Assume valid data constraints
        assume(len(permission_data['name'].strip()) > 0)
        assume(len(permission_data['codename'].strip()) > 0)
        assume(len(role_data['name'].strip()) > 0)
        assume(permission_data['codename'].replace('_', '').replace('-', '').isalnum())
        
        content_type = self.content_types[0]  # Use first content type for simplicity
        
        # Make names unique to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        unique_codename = f"{permission_data['codename'].strip().lower()}_{unique_id}"
        unique_role_name = f"{role_data['name'].strip()}_{unique_id}"
        
        # Handle None conditions - convert to empty dict as per model default
        if conditions is None:
            conditions = {}
        
        # Create permission and role
        permission = Permission.objects.create(
            name=permission_data['name'].strip(),
            codename=unique_codename,
            content_type=content_type,
            description=permission_data['description']
        )
        
        role = Role.objects.create(
            name=unique_role_name,
            description=role_data['description']
        )
        
        # Create role-permission relationship
        role_permission = RolePermission.objects.create(
            role=role,
            permission=permission,
            granted=granted,
            conditions=conditions
        )
        
        # Verify relationship integrity
        self._verify_role_permission_relationship_integrity(
            role_permission, role, permission, granted, conditions
        )
        
        # Verify cascading behavior
        self._verify_role_permission_cascading_integrity(role_permission, role, permission)
    
    @given(
        role_data_strategy(),
        st.one_of(st.none(), st.datetimes(min_value=timezone.now().replace(tzinfo=None) + timedelta(days=1))),
        st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_user_role_assignment_integrity(self, role_data, expires_at, is_active):
        """
        Property: Any valid user-role assignment should maintain
        referential integrity and handle expiration correctly.
        """
        # Assume valid data constraints
        assume(len(role_data['name'].strip()) > 0)
        
        # Create test user and role with unique names
        unique_id = str(uuid.uuid4())[:8]
        user = TestDataFactory.create_user(username=f"test_user_{unique_id}")
        role = Role.objects.create(
            name=f"{role_data['name'].strip()}_{unique_id}",
            description=role_data['description']
        )
        
        # Convert naive datetime to timezone-aware if needed
        if expires_at is not None:
            expires_at = timezone.make_aware(expires_at) if timezone.is_naive(expires_at) else expires_at
        
        # Create user-role assignment
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=self.admin_user,
            expires_at=expires_at,
            is_active=is_active
        )
        
        # Verify assignment integrity
        self._verify_user_role_assignment_integrity(
            user_role, user, role, expires_at, is_active
        )
        
        # Verify cascading behavior
        self._verify_user_role_cascading_integrity(user_role, user, role)
    
    @given(
        st.lists(permission_data_strategy(), min_size=1, max_size=5),
        st.lists(role_data_strategy(), min_size=1, max_size=3)
    )
    @settings(max_examples=50, deadline=None)
    def test_complex_permission_system_integrity(self, permissions_data, roles_data):
        """
        Property: Complex permission systems with multiple permissions,
        roles, and relationships should maintain complete integrity.
        """
        # Assume valid data constraints
        for perm_data in permissions_data:
            assume(len(perm_data['name'].strip()) > 0)
            assume(len(perm_data['codename'].strip()) > 0)
            assume(perm_data['codename'].replace('_', '').replace('-', '').isalnum())
        
        for role_data in roles_data:
            assume(len(role_data['name'].strip()) > 0)
        
        # Ensure unique codenames and role names
        unique_id = str(uuid.uuid4())[:8]
        codenames = [f"{p['codename'].strip().lower()}_{unique_id}_{i}" for i, p in enumerate(permissions_data)]
        role_names = [f"{r['name'].strip()}_{unique_id}_{i}" for i, r in enumerate(roles_data)]
        
        content_type = self.content_types[0]  # Use first content type for simplicity
        
        # Create permissions
        permissions = []
        for i, perm_data in enumerate(permissions_data):
            permission = Permission.objects.create(
                name=f"{perm_data['name'].strip()}_{unique_id}_{i}",
                codename=codenames[i],
                content_type=content_type,
                description=perm_data['description']
            )
            permissions.append(permission)
        
        # Create roles
        roles = []
        for i, role_data in enumerate(roles_data):
            role = Role.objects.create(
                name=role_names[i],
                description=role_data['description']
            )
            roles.append(role)
        
        # Create role-permission relationships
        role_permissions = []
        for role in roles:
            for permission in permissions:
                granted = True  # Simplify for testing
                conditions = {}  # Simplify for testing
                
                role_permission = RolePermission.objects.create(
                    role=role,
                    permission=permission,
                    granted=granted,
                    conditions=conditions
                )
                role_permissions.append(role_permission)
        
        # Create users and assign roles
        users = []
        user_roles = []
        for i, role in enumerate(roles):
            user = TestDataFactory.create_user(username=f"test_user_{unique_id}_{i}")
            users.append(user)
            
            user_role = UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=self.admin_user
            )
            user_roles.append(user_role)
        
        # Verify complete system integrity
        self._verify_complete_system_integrity(
            permissions, roles, role_permissions, users, user_roles
        )
    
    def _verify_permission_storage_integrity(self, permission, permission_data, content_type, unique_codename):
        """Verify that permission is stored correctly"""
        # Reload from database
        stored_permission = Permission.objects.get(id=permission.id)
        
        # Verify all fields are stored correctly
        self.assertEqual(stored_permission.name, permission_data['name'].strip())
        self.assertEqual(stored_permission.codename, unique_codename)
        self.assertEqual(stored_permission.content_type, content_type)
        self.assertEqual(stored_permission.description, permission_data['description'])
        
        # Verify timestamps
        self.assertIsNotNone(stored_permission.created_at)
        self.assertIsNotNone(stored_permission.updated_at)
        self.assertLessEqual(stored_permission.created_at, stored_permission.updated_at)
        
        # Verify string representation
        expected_str = f"{content_type.app_label}.{unique_codename}"
        self.assertEqual(str(stored_permission), expected_str)
    
    def _verify_permission_database_constraints(self, permission):
        """Verify database constraints are enforced"""
        # Test unique constraint on (content_type, codename)
        try:
            with transaction.atomic():
                Permission.objects.create(
                    name="Duplicate Permission",
                    codename=permission.codename,
                    content_type=permission.content_type,
                    description="This should fail"
                )
            # If we get here, the constraint didn't work
            self.fail("Expected IntegrityError for duplicate permission")
        except IntegrityError:
            # This is expected - constraint is working
            pass
    
    def _verify_permission_referential_integrity(self, permission):
        """Verify referential integrity with content types"""
        # Verify content type relationship
        self.assertIsNotNone(permission.content_type)
        self.assertTrue(ContentType.objects.filter(id=permission.content_type.id).exists())
        
        # Verify reverse relationship
        self.assertIn(permission, permission.content_type.dynamic_permissions.all())
    
    def _verify_role_storage_integrity(self, role, role_data):
        """Verify that role is stored correctly"""
        # Reload from database
        stored_role = Role.objects.get(id=role.id)
        
        # Verify all fields are stored correctly
        self.assertEqual(stored_role.name, role_data['name'].strip())
        self.assertEqual(stored_role.description, role_data['description'])
        self.assertTrue(stored_role.is_active)  # Default value
        
        # Verify timestamps
        self.assertIsNotNone(stored_role.created_at)
        self.assertIsNotNone(stored_role.updated_at)
        self.assertLessEqual(stored_role.created_at, stored_role.updated_at)
        
        # Verify string representation
        self.assertEqual(str(stored_role), role_data['name'].strip())
    
    def _verify_role_database_constraints(self, role):
        """Verify database constraints are enforced"""
        # Test unique constraint on name
        try:
            with transaction.atomic():
                Role.objects.create(
                    name=role.name,  # Duplicate name should fail
                    description="This should fail"
                )
            # If we get here, the constraint didn't work
            self.fail("Expected IntegrityError for duplicate role name")
        except IntegrityError:
            # This is expected - constraint is working
            pass
    
    def _verify_role_referential_integrity(self, role):
        """Verify referential integrity for roles"""
        # Verify role exists in database
        self.assertTrue(Role.objects.filter(id=role.id).exists())
        
        # Verify permissions relationship (empty initially)
        self.assertEqual(role.permissions.count(), 0)
    
    def _verify_role_permission_relationship_integrity(self, role_permission, role, permission, granted, conditions):
        """Verify role-permission relationship integrity"""
        # Reload from database
        stored_rp = RolePermission.objects.get(id=role_permission.id)
        
        # Verify relationship fields
        self.assertEqual(stored_rp.role, role)
        self.assertEqual(stored_rp.permission, permission)
        self.assertEqual(stored_rp.granted, granted)
        self.assertEqual(stored_rp.conditions, conditions)
        
        # Verify timestamp
        self.assertIsNotNone(stored_rp.created_at)
        
        # Verify reverse relationships
        self.assertIn(permission, role.permissions.all())
        
        # Verify string representation
        status = "granted" if granted else "denied"
        expected_str = f"{role.name} - {permission.codename} ({status})"
        self.assertEqual(str(stored_rp), expected_str)
    
    def _verify_role_permission_cascading_integrity(self, role_permission, role, permission):
        """Verify cascading behavior maintains integrity"""
        # Store IDs for verification
        rp_id = role_permission.id
        
        # Delete role - should cascade delete role_permission
        role.delete()
        self.assertFalse(RolePermission.objects.filter(id=rp_id).exists())
        
        # Permission should still exist
        self.assertTrue(Permission.objects.filter(id=permission.id).exists())
    
    def _verify_user_role_assignment_integrity(self, user_role, user, role, expires_at, is_active):
        """Verify user-role assignment integrity"""
        # Reload from database
        stored_ur = UserRole.objects.get(id=user_role.id)
        
        # Verify assignment fields
        self.assertEqual(stored_ur.user, user)
        self.assertEqual(stored_ur.role, role)
        self.assertEqual(stored_ur.assigned_by, self.admin_user)
        self.assertEqual(stored_ur.expires_at, expires_at)
        self.assertEqual(stored_ur.is_active, is_active)
        
        # Verify timestamps
        self.assertIsNotNone(stored_ur.assigned_at)
        
        # Verify expiration logic
        if expires_at:
            if expires_at > timezone.now():
                self.assertFalse(stored_ur.is_expired)
            # Note: We can't test past expiration in property tests due to time constraints
        else:
            self.assertFalse(stored_ur.is_expired)
        
        # Verify reverse relationships
        self.assertIn(role, user.roles.all())
        
        # Verify string representation
        expected_str = f"{user.username} - {role.name}"
        self.assertEqual(str(stored_ur), expected_str)
    
    def _verify_user_role_cascading_integrity(self, user_role, user, role):
        """Verify cascading behavior maintains integrity"""
        # Store IDs for verification
        ur_id = user_role.id
        
        # Delete user - should cascade delete user_role
        user.delete()
        self.assertFalse(UserRole.objects.filter(id=ur_id).exists())
        
        # Role should still exist
        self.assertTrue(Role.objects.filter(id=role.id).exists())
    
    def _verify_complete_system_integrity(self, permissions, roles, role_permissions, users, user_roles):
        """Verify integrity of complete permission system"""
        # Verify all objects exist in database
        for permission in permissions:
            self.assertTrue(Permission.objects.filter(id=permission.id).exists())
        
        for role in roles:
            self.assertTrue(Role.objects.filter(id=role.id).exists())
        
        for role_permission in role_permissions:
            self.assertTrue(RolePermission.objects.filter(id=role_permission.id).exists())
        
        for user in users:
            self.assertTrue(User.objects.filter(id=user.id).exists())
        
        for user_role in user_roles:
            self.assertTrue(UserRole.objects.filter(id=user_role.id).exists())
        
        # Verify relationship counts
        total_role_permissions = sum(role.permissions.count() for role in roles)
        self.assertEqual(total_role_permissions, len(role_permissions))
        
        total_user_roles = sum(user.roles.count() for user in users)
        self.assertEqual(total_user_roles, len(user_roles))
        
        # Verify no orphaned records
        self.assertNoOrphanedRecords(RolePermission, 'role')
        self.assertNoOrphanedRecords(RolePermission, 'permission')
        self.assertNoOrphanedRecords(UserRole, 'user')
        self.assertNoOrphanedRecords(UserRole, 'role')
        
        # Verify database integrity
        self.assertDatabaseIntegrity(Permission)
        self.assertDatabaseIntegrity(Role)
        self.assertDatabaseIntegrity(RolePermission)
        self.assertDatabaseIntegrity(UserRole)
        
        # Test permission evaluation works correctly
        for user in users:
            # Should be able to get permissions without errors
            permissions_count = user.get_dynamic_permissions().count()
            self.assertGreaterEqual(permissions_count, 0)
            
            # Permission checking should work
            for permission in permissions:
                # Should not raise exceptions
                has_perm = user.has_dynamic_permission(permission.codename)
                self.assertIsInstance(has_perm, bool)


class PermissionStorageIntegrityTransactionTest(TransactionTestCase):
    """
    Transaction-based tests for permission storage integrity.
    Tests behavior under transaction rollback scenarios.
    """
    
    @pytest.mark.property
    def test_permission_storage_transaction_integrity(self):
        """
        **Property 12: Permission Storage Integrity**
        **Validates: Requirements 3.1**
        
        Test that permission storage maintains integrity even when
        transactions are rolled back.
        """
        content_type = ContentType.objects.get_for_model(User)
        
        # Test successful transaction
        with transaction.atomic():
            permission = Permission.objects.create(
                name="Test Permission",
                codename="test_perm",
                content_type=content_type,
                description="Test description"
            )
            permission_id = permission.id
        
        # Verify permission was saved
        self.assertTrue(Permission.objects.filter(id=permission_id).exists())
        
        # Test rolled back transaction
        try:
            with transaction.atomic():
                permission2 = Permission.objects.create(
                    name="Test Permission 2",
                    codename="test_perm_2",
                    content_type=content_type,
                    description="Test description 2"
                )
                permission2_id = permission2.id
                
                # Force rollback by raising exception
                raise IntegrityError("Forced rollback")
        except IntegrityError:
            pass
        
        # Verify permission2 was not saved due to rollback
        self.assertFalse(Permission.objects.filter(id=permission2_id).exists())
        
        # Verify original permission still exists
        self.assertTrue(Permission.objects.filter(id=permission_id).exists())
    
    @pytest.mark.property
    def test_role_permission_transaction_integrity(self):
        """
        Test that role-permission relationships maintain integrity
        under transaction rollback scenarios.
        """
        content_type = ContentType.objects.get_for_model(User)
        
        # Create base objects
        permission = Permission.objects.create(
            name="Test Permission",
            codename="test_perm",
            content_type=content_type
        )
        role = Role.objects.create(name="Test Role")
        
        # Test successful transaction
        with transaction.atomic():
            role_permission = RolePermission.objects.create(
                role=role,
                permission=permission,
                granted=True
            )
            rp_id = role_permission.id
        
        # Verify relationship was saved
        self.assertTrue(RolePermission.objects.filter(id=rp_id).exists())
        self.assertIn(permission, role.permissions.all())
        
        # Test rolled back transaction
        try:
            with transaction.atomic():
                role_permission2 = RolePermission.objects.create(
                    role=role,
                    permission=permission,
                    granted=False  # This should create a duplicate and fail
                )
                # This will fail due to unique constraint, causing rollback
        except IntegrityError:
            pass
        
        # Verify original relationship still exists and is unchanged
        self.assertTrue(RolePermission.objects.filter(id=rp_id).exists())
        stored_rp = RolePermission.objects.get(id=rp_id)
        self.assertTrue(stored_rp.granted)  # Should still be True
        
        # Verify only one relationship exists
        self.assertEqual(RolePermission.objects.filter(role=role, permission=permission).count(), 1)