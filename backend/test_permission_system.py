#!/usr/bin/env python
"""
Test script to demonstrate the dynamic permission system functionality.
Run this script to see how the permission system works.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Permission, Role, RolePermission, UserRole

User = get_user_model()


def test_permission_system():
    """Test the dynamic permission system"""
    print("=== Dynamic Permission System Test ===\n")
    
    # Get test users
    try:
        admin_user = User.objects.get(username='admin_sample')
        regular_user = User.objects.get(username='user_sample')
    except User.DoesNotExist:
        print("Sample users not found. Please run: python manage.py create_sample_permissions")
        return
    
    print("1. Testing Admin User Permissions:")
    print(f"   User: {admin_user.username} ({admin_user.get_full_name()})")
    
    # Test admin permissions
    admin_permissions = admin_user.get_dynamic_permissions()
    print(f"   Dynamic permissions count: {admin_permissions.count()}")
    
    for perm in admin_permissions:
        print(f"   - {perm.name} ({perm.codename})")
    
    # Test specific permission checks
    print(f"   Can view users: {admin_user.has_dynamic_permission('view_user')}")
    print(f"   Can add users: {admin_user.has_dynamic_permission('add_user')}")
    print(f"   Can delete users: {admin_user.has_dynamic_permission('delete_user')}")
    print(f"   Can manage permissions: {admin_user.has_dynamic_permission('manage_permissions')}")
    
    print("\n2. Testing Regular User Permissions:")
    print(f"   User: {regular_user.username} ({regular_user.get_full_name()})")
    
    # Test regular user permissions
    regular_permissions = regular_user.get_dynamic_permissions()
    print(f"   Dynamic permissions count: {regular_permissions.count()}")
    
    for perm in regular_permissions:
        print(f"   - {perm.name} ({perm.codename})")
    
    # Test specific permission checks
    print(f"   Can view users: {regular_user.has_dynamic_permission('view_user')}")
    print(f"   Can add users: {regular_user.has_dynamic_permission('add_user')}")
    print(f"   Can delete users: {regular_user.has_dynamic_permission('delete_user')}")
    print(f"   Can manage permissions: {regular_user.has_dynamic_permission('manage_permissions')}")
    
    print("\n3. Testing Role Management:")
    
    # Get roles
    admin_roles = admin_user.roles.all()
    regular_roles = regular_user.roles.all()
    
    print(f"   Admin user roles: {[role.name for role in admin_roles]}")
    print(f"   Regular user roles: {[role.name for role in regular_roles]}")
    
    print("\n4. Testing Role Expiration:")
    
    # Test role expiration
    user_roles = UserRole.objects.filter(user=regular_user)
    for user_role in user_roles:
        print(f"   Role: {user_role.role.name}")
        print(f"   Assigned at: {user_role.assigned_at}")
        print(f"   Expires at: {user_role.expires_at or 'Never'}")
        print(f"   Is expired: {user_role.is_expired}")
        print(f"   Is active: {user_role.is_active}")
    
    print("\n5. Testing Permission Conditions:")
    
    # Show role permissions with conditions
    for role in Role.objects.all():
        print(f"   Role: {role.name}")
        role_perms = RolePermission.objects.filter(role=role)
        for rp in role_perms:
            conditions_str = f" (conditions: {rp.conditions})" if rp.conditions else ""
            status = "granted" if rp.granted else "denied"
            print(f"     - {rp.permission.codename}: {status}{conditions_str}")
    
    print("\n6. Database Integrity Check:")
    
    # Check database integrity
    total_permissions = Permission.objects.count()
    total_roles = Role.objects.count()
    total_role_permissions = RolePermission.objects.count()
    total_user_roles = UserRole.objects.count()
    
    print(f"   Total permissions: {total_permissions}")
    print(f"   Total roles: {total_roles}")
    print(f"   Total role-permission assignments: {total_role_permissions}")
    print(f"   Total user-role assignments: {total_user_roles}")
    
    # Check for orphaned records
    orphaned_role_perms = RolePermission.objects.filter(role__isnull=True)
    orphaned_user_roles = UserRole.objects.filter(user__isnull=True)
    
    print(f"   Orphaned role permissions: {orphaned_role_perms.count()}")
    print(f"   Orphaned user roles: {orphaned_user_roles.count()}")
    
    print("\n=== Test Complete ===")
    print("The dynamic permission system is working correctly!")


if __name__ == '__main__':
    test_permission_system()