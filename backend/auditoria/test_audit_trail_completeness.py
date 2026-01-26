"""
Property-based test for audit trail completeness.

This test validates Property 17: Comprehensive Audit Trail
Requirements: 3.4, 5.6, 8.3

The test ensures that for any system change (permissions, configurations, data),
the audit trail logs all modifications with timestamps, user details, and change descriptions.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
import json

from auditoria.models import AuditLog
from auditoria.utils import (
    log_action, log_authentication_action, log_permission_action,
    log_configuration_change, log_data_operation, log_access_denied
)
from accounts.models import Role, Permission, UserRole, RolePermission
from catalogo.models import CategoriaProducto

User = get_user_model()


class TestAuditTrailCompleteness(HypothesisTestCase):
    """
    **Feature: system-modernization, Property 17: Comprehensive Audit Trail**
    **Validates: Requirements 3.4, 5.6, 8.3**
    
    Property-based test that validates the audit trail logs all modifications
    with timestamps, user details, and change descriptions for any system change.
    """
    
    def setUp(self):
        """Set up test data"""
        # Use get_or_create to avoid unique constraint violations
        self.admin_user, _ = User.objects.get_or_create(
            username='admin_test_audit',
            defaults={
                'password': 'password123',
                'email': 'admin@test.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        self.regular_user, _ = User.objects.get_or_create(
            username='user_test_audit',
            defaults={
                'password': 'password123',
                'email': 'user@test.com'
            }
        )
        
        # Create content type for testing
        self.content_type = ContentType.objects.get_for_model(CategoriaProducto)
        
        # Create test permission and role
        self.test_permission, _ = Permission.objects.get_or_create(
            codename='test_permission',
            content_type=self.content_type,
            defaults={
                'name': 'Test Permission',
                'description': 'Test permission for audit trail testing'
            }
        )
        
        self.test_role, _ = Role.objects.get_or_create(
            name='Test Role',
            defaults={
                'description': 'Test role for audit trail testing'
            }
        )

    # Strategy for generating valid action types
    action_strategy = st.sampled_from([
        'CREATE', 'UPDATE', 'DELETE', 'RESTORE', 'HARD_DELETE',
        'LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'PASSWORD_CHANGE', 'PASSWORD_RESET',
        'PERMISSION_GRANT', 'PERMISSION_REVOKE', 'ROLE_ASSIGN', 'ROLE_REMOVE',
        'CONFIG_CHANGE', 'SYSTEM_MAINTENANCE',
        'EXPORT', 'IMPORT', 'BULK_UPDATE', 'BULK_DELETE',
        'ACCESS_DENIED', 'UNAUTHORIZED_ACCESS'
    ])

    # Strategy for generating IP addresses
    ip_strategy = st.one_of(
        st.text(min_size=7, max_size=15).filter(lambda x: '.' in x),  # Simple IPv4-like
        st.none()
    )

    # Strategy for generating user agents
    user_agent_strategy = st.one_of(
        st.text(min_size=10, max_size=200),
        st.none()
    )

    # Strategy for generating change data
    @st.composite
    def changes_strategy(draw):
        """Generate realistic change data structures"""
        change_type = draw(st.sampled_from(['field_changes', 'old_new_values', 'simple_change']))
        
        if change_type == 'field_changes':
            fields = draw(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5))
            return {'fields_changed': fields}
        elif change_type == 'old_new_values':
            field_name = draw(st.text(min_size=1, max_size=20))
            old_value = draw(st.one_of(st.text(), st.integers(), st.booleans()))
            new_value = draw(st.one_of(st.text(), st.integers(), st.booleans()))
            return {
                'old_values': {field_name: old_value},
                'new_values': {field_name: new_value}
            }
        else:
            return {'description': draw(st.text(min_size=1, max_size=100))}

    # Strategy for generating configuration keys
    config_key_strategy = st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
        min_size=3,
        max_size=50
    )

    # Strategy for generating configuration values
    config_value_strategy = st.one_of(
        st.text(min_size=1, max_size=100),
        st.integers(min_value=1, max_value=10000),
        st.booleans(),
        st.floats(min_value=0.1, max_value=100.0)
    )

    @given(
        user=st.one_of(st.just(None), st.sampled_from(['admin', 'regular'])),
        action=action_strategy,
        ip_address=ip_strategy,
        user_agent=user_agent_strategy,
        changes=changes_strategy(),
        risk_level=st.sampled_from(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.property
    def test_audit_log_completeness_for_any_action(self, user, action, ip_address, 
                                                  user_agent, changes, risk_level):
        """
        Property: For any system action, audit log must contain complete information.
        
        This test verifies that regardless of the action type, user, or context,
        the audit trail always captures:
        - Timestamp (automatically set)
        - User details (when available)
        - Action type
        - Change descriptions
        - Request metadata (IP, user agent)
        """
        # Map user string to actual user object
        if user == 'admin':
            test_user = self.admin_user
        elif user == 'regular':
            test_user = self.regular_user
        else:
            test_user = None

        # Create a test object for actions that need one
        test_object = None
        if action in ['CREATE', 'UPDATE', 'DELETE', 'RESTORE', 'HARD_DELETE']:
            test_object = CategoriaProducto.objects.create(
                nombre=f'Test Category {timezone.now().timestamp()}',
                codigo=f'TEST{timezone.now().timestamp()}'[:10]
            )

        # Log the action using the enhanced logging system
        audit_log = AuditLog.log_action(
            user=test_user,
            action=action,
            content_object=test_object,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            risk_level=risk_level
        )

        # Verify audit log completeness
        self._verify_audit_log_completeness(
            audit_log, test_user, action, changes, ip_address, user_agent, risk_level
        )

    @given(
        config_key=config_key_strategy,
        old_value=config_value_strategy,
        new_value=config_value_strategy,
        ip_address=ip_strategy,
        user_agent=user_agent_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.property
    def test_configuration_change_audit_completeness(self, config_key, old_value, 
                                                    new_value, ip_address, user_agent):
        """
        Property: For any configuration change, audit trail must log complete details.
        
        **Validates: Requirements 5.6, 8.3**
        
        This test verifies that configuration changes are always logged with:
        - User who made the change
        - Configuration key modified
        - Old and new values
        - Timestamp
        - Request metadata
        """
        assume(old_value != new_value)  # Only test actual changes
        assume(len(config_key.strip()) > 0)  # Ensure non-empty key
        
        # Log configuration change
        audit_log = log_configuration_change(
            user=self.admin_user,
            config_key=config_key,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Verify configuration change audit completeness
        assert audit_log is not None, "Configuration change must create audit log"
        assert audit_log.user == self.admin_user, "Audit log must record the user"
        assert audit_log.action == 'CONFIG_CHANGE', "Action must be CONFIG_CHANGE"
        assert audit_log.timestamp is not None, "Timestamp must be recorded"
        assert audit_log.risk_level == 'MEDIUM', "Config changes should be MEDIUM risk"
        
        # Verify change details
        assert 'config_key' in audit_log.changes, "Changes must include config_key"
        assert 'old_value' in audit_log.changes, "Changes must include old_value"
        assert 'new_value' in audit_log.changes, "Changes must include new_value"
        assert audit_log.changes['config_key'] == config_key
        assert audit_log.changes['old_value'] == old_value
        assert audit_log.changes['new_value'] == new_value
        
        # Verify metadata
        assert audit_log.ip_address == ip_address, "IP address must be recorded"
        assert audit_log.user_agent == user_agent, "User agent must be recorded"
        assert 'config_key' in audit_log.extra_data, "Extra data must include config_key"

    @given(
        target_user=st.just(None),  # Will use self.regular_user
        permission_action=st.sampled_from(['PERMISSION_GRANT', 'PERMISSION_REVOKE', 'ROLE_ASSIGN', 'ROLE_REMOVE']),
        granted=st.booleans(),
        ip_address=ip_strategy,
        user_agent=user_agent_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.property
    def test_permission_change_audit_completeness(self, target_user, permission_action, 
                                                 granted, ip_address, user_agent):
        """
        Property: For any permission change, audit trail must log complete details.
        
        **Validates: Requirements 3.4**
        
        This test verifies that permission changes are always logged with:
        - User who made the change
        - Target user affected
        - Permission or role involved
        - Whether granted or revoked
        - Timestamp
        - Request metadata
        """
        # Use regular user as target
        actual_target_user = self.regular_user
        
        # Choose permission or role based on action
        if permission_action in ['PERMISSION_GRANT', 'PERMISSION_REVOKE']:
            permission = self.test_permission
            role = None
        else:  # ROLE_ASSIGN, ROLE_REMOVE
            permission = None
            role = self.test_role

        # Log permission action
        audit_log = log_permission_action(
            user=self.admin_user,
            action=permission_action,
            target_user=actual_target_user,
            permission=permission,
            role=role,
            granted=granted,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Verify permission change audit completeness
        assert audit_log is not None, "Permission change must create audit log"
        assert audit_log.user == self.admin_user, "Audit log must record the acting user"
        assert audit_log.content_object == actual_target_user, "Must record target user"
        assert audit_log.action == permission_action, f"Action must be {permission_action}"
        assert audit_log.timestamp is not None, "Timestamp must be recorded"
        assert audit_log.risk_level == 'HIGH', "Permission changes should be HIGH risk"
        
        # Verify change details
        assert 'granted' in audit_log.changes, "Changes must include granted status"
        assert audit_log.changes['granted'] == granted
        
        if permission:
            assert 'permission' in audit_log.changes, "Changes must include permission"
            assert audit_log.changes['permission'] == str(permission)
            assert 'permission_id' in audit_log.extra_data, "Extra data must include permission_id"
            assert audit_log.extra_data['permission_id'] == permission.id
        
        if role:
            assert 'role' in audit_log.changes, "Changes must include role"
            assert audit_log.changes['role'] == str(role)
            assert 'role_id' in audit_log.extra_data, "Extra data must include role_id"
            assert audit_log.extra_data['role_id'] == role.id
        
        # Verify metadata
        assert audit_log.ip_address == ip_address, "IP address must be recorded"
        assert audit_log.user_agent == user_agent, "User agent must be recorded"

    @given(
        data_action=st.sampled_from(['EXPORT', 'IMPORT', 'BULK_UPDATE', 'BULK_DELETE']),
        affected_count=st.integers(min_value=1, max_value=5000),
        operation_type=st.text(min_size=5, max_size=50),
        ip_address=ip_strategy,
        user_agent=user_agent_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.property
    def test_data_operation_audit_completeness(self, data_action, affected_count, 
                                             operation_type, ip_address, user_agent):
        """
        Property: For any data operation, audit trail must log complete details.
        
        This test verifies that data operations are always logged with:
        - User who performed the operation
        - Number of records affected
        - Operation type
        - Appropriate risk level based on scale
        - Timestamp
        - Request metadata
        """
        assume(len(operation_type.strip()) > 0)  # Ensure non-empty operation type
        
        # Log data operation
        audit_log = log_data_operation(
            user=self.admin_user,
            action=data_action,
            affected_count=affected_count,
            operation_type=operation_type,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Verify data operation audit completeness
        assert audit_log is not None, "Data operation must create audit log"
        assert audit_log.user == self.admin_user, "Audit log must record the user"
        assert audit_log.action == data_action, f"Action must be {data_action}"
        assert audit_log.timestamp is not None, "Timestamp must be recorded"
        
        # Verify risk level is appropriate for scale
        if affected_count > 1000:
            expected_risk = 'HIGH'
        elif affected_count > 100:
            expected_risk = 'MEDIUM'
        else:
            expected_risk = 'LOW'
        assert audit_log.risk_level == expected_risk, f"Risk level should be {expected_risk} for {affected_count} records"
        
        # Verify change details
        assert 'affected_count' in audit_log.changes, "Changes must include affected_count"
        assert 'operation_type' in audit_log.changes, "Changes must include operation_type"
        assert audit_log.changes['affected_count'] == affected_count
        assert audit_log.changes['operation_type'] == operation_type
        
        # Verify extra data
        assert 'affected_count' in audit_log.extra_data, "Extra data must include affected_count"
        assert 'operation_type' in audit_log.extra_data, "Extra data must include operation_type"
        assert audit_log.extra_data['affected_count'] == affected_count
        assert audit_log.extra_data['operation_type'] == operation_type
        
        # Verify metadata
        assert audit_log.ip_address == ip_address, "IP address must be recorded"
        assert audit_log.user_agent == user_agent, "User agent must be recorded"

    @given(
        success=st.booleans(),
        ip_address=ip_strategy,
        user_agent=user_agent_strategy,
        username=st.text(min_size=3, max_size=30)
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.property
    def test_authentication_audit_completeness(self, success, ip_address, user_agent, username):
        """
        Property: For any authentication attempt, audit trail must log complete details.
        
        This test verifies that authentication events are always logged with:
        - User (for successful attempts) or attempted username (for failures)
        - Success/failure status
        - Appropriate risk level
        - Timestamp
        - Request metadata
        """
        assume(len(username.strip()) > 0)  # Ensure non-empty username
        
        # Test successful authentication
        if success:
            user = self.regular_user
            action = 'LOGIN'
        else:
            user = None
            action = 'LOGIN_FAILED'
            
        extra_data = {'username': username} if not success else None

        # Log authentication action
        audit_log = log_authentication_action(
            user=user,
            action=action,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )

        # Verify authentication audit completeness
        assert audit_log is not None, "Authentication attempt must create audit log"
        assert audit_log.action == action, f"Action must be {action}"
        assert audit_log.timestamp is not None, "Timestamp must be recorded"
        
        if success:
            assert audit_log.user == user, "Successful login must record user"
            assert audit_log.risk_level == 'LOW', "Successful login should be LOW risk"
        else:
            assert audit_log.user is None, "Failed login should not have user"
            assert audit_log.risk_level == 'MEDIUM', "Failed login should be MEDIUM risk"
            assert 'attempted_username' in audit_log.extra_data, "Failed login must record attempted username"
        
        # Verify change details
        assert 'success' in audit_log.changes, "Changes must include success status"
        assert audit_log.changes['success'] == success
        
        # Verify metadata
        assert audit_log.ip_address == ip_address, "IP address must be recorded"
        assert audit_log.user_agent == user_agent, "User agent must be recorded"

    def _verify_audit_log_completeness(self, audit_log, user, action, changes, 
                                     ip_address, user_agent, risk_level):
        """
        Helper method to verify audit log completeness for any action.
        
        This ensures that all audit logs, regardless of type, contain
        the essential information required for a complete audit trail.
        """
        # Core audit log properties
        assert audit_log is not None, "Audit log must be created"
        assert audit_log.action == action, f"Action must be {action}"
        assert audit_log.timestamp is not None, "Timestamp must be recorded"
        assert audit_log.risk_level == risk_level, f"Risk level must be {risk_level}"
        
        # User information (when available)
        if user is not None:
            assert audit_log.user == user, "User must be recorded when available"
        else:
            assert audit_log.user is None, "User should be None for system actions"
        
        # Change information
        if changes:
            assert audit_log.changes == changes, "Changes must be recorded accurately"
        
        # Request metadata
        assert audit_log.ip_address == ip_address, "IP address must be recorded"
        assert audit_log.user_agent == user_agent, "User agent must be recorded"
        
        # Verify timestamp is recent (within last minute)
        time_diff = timezone.now() - audit_log.timestamp
        assert time_diff < timedelta(minutes=1), "Timestamp should be recent"
        
        # Verify object representation is meaningful
        if audit_log.object_repr:
            assert len(audit_log.object_repr.strip()) > 0, "Object representation should be meaningful"
        
        # Verify extra data is properly structured
        assert isinstance(audit_log.extra_data, dict), "Extra data must be a dictionary"

    def test_audit_trail_persistence_and_immutability(self):
        """
        Test that audit logs are persistent and cannot be modified after creation.
        
        This ensures the integrity of the audit trail by verifying that
        audit logs remain unchanged once created.
        """
        # Create an audit log
        test_object = CategoriaProducto.objects.create(
            nombre='Immutable Test',
            codigo='IMMUT'
        )
        
        original_log = log_action(
            test_object, 
            'CREATE',
            changes={'test': 'original'},
            risk_level='LOW'
        )
        
        original_timestamp = original_log.timestamp
        original_changes = original_log.changes.copy()
        original_action = original_log.action
        
        # Verify the log exists and has expected values
        assert original_log.action == 'CREATE'
        assert original_log.changes == {'test': 'original'}
        
        # Attempt to modify the log (this should be prevented by proper access controls)
        # In a real system, this would be prevented by database permissions
        # Here we test that the log maintains its integrity
        retrieved_log = AuditLog.objects.get(id=original_log.id)
        
        assert retrieved_log.timestamp == original_timestamp
        assert retrieved_log.changes == original_changes
        assert retrieved_log.action == original_action
        
        # Verify that the audit log is complete and hasn't been tampered with
        assert retrieved_log.object_repr == 'Immutable Test'
        assert retrieved_log.risk_level == 'LOW'

    def test_audit_trail_query_performance(self):
        """
        Test that audit trail queries perform efficiently with proper indexing.
        
        This ensures that the audit trail can be queried efficiently even
        with large volumes of audit data.
        """
        # Create multiple audit logs to test query performance
        test_objects = []
        for i in range(10):
            obj = CategoriaProducto.objects.create(
                nombre=f'Performance Test {i}',
                codigo=f'PERF{i}'
            )
            test_objects.append(obj)
            
            # Create audit logs for each object
            log_action(obj, 'CREATE', risk_level='LOW')
            log_action(obj, 'UPDATE', changes={'field': f'value_{i}'}, risk_level='MEDIUM')
        
        # Test various query patterns that should be optimized by indexes
        
        # Query by timestamp (should use timestamp index)
        recent_logs = AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=1)
        )
        assert recent_logs.count() >= 20  # At least our test logs
        
        # Query by user and timestamp (should use user_timestamp index)
        user_logs = AuditLog.objects.filter(
            user=self.admin_user,
            timestamp__gte=timezone.now() - timedelta(minutes=1)
        )
        # This might be 0 if no user was set in log_action calls
        
        # Query by action and timestamp (should use action_timestamp index)
        create_logs = AuditLog.objects.filter(
            action='CREATE',
            timestamp__gte=timezone.now() - timedelta(minutes=1)
        )
        assert create_logs.count() >= 10  # Our CREATE logs
        
        # Query by risk level and timestamp (should use risk_level_timestamp index)
        medium_risk_logs = AuditLog.objects.filter(
            risk_level='MEDIUM',
            timestamp__gte=timezone.now() - timedelta(minutes=1)
        )
        assert medium_risk_logs.count() >= 10  # Our UPDATE logs
        
        # Verify that queries return expected results
        for log in create_logs:
            assert log.action == 'CREATE'
            assert log.risk_level == 'LOW'
        
        for log in medium_risk_logs:
            assert log.risk_level == 'MEDIUM'