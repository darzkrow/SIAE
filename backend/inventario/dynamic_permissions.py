"""
Dynamic Permission System for GSIH API endpoints.

This module provides a flexible, database-driven permission system that evaluates
user permissions dynamically and handles permission conflicts according to a
defined precedence hierarchy.
"""

from rest_framework.permissions import BasePermission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DynamicPermission(BasePermission):
    """
    Dynamic permission class that evaluates permissions from database.
    
    This permission class:
    - Evaluates user permissions dynamically from the database
    - Supports granular control per module and action
    - Follows a defined precedence hierarchy for conflict resolution
    - Caches permission evaluations for performance
    """
    
    # Permission actions mapping
    ACTION_MAP = {
        'list': 'view',
        'retrieve': 'view',
        'create': 'add',
        'update': 'change',
        'partial_update': 'change',
        'destroy': 'delete',
        'bulk_create': 'add',
        'bulk_update': 'change',
        'bulk_delete': 'delete',
    }
    
    def has_permission(self, request, view):
        """
        Check if user has permission for the requested action.
        """
        # Allow unauthenticated users for safe methods if configured
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have permission
        if request.user.is_superuser:
            return True
        
        # Get the model and action
        model = getattr(view, 'queryset', None)
        if model is not None:
            model = model.model
        else:
            # Fallback for viewsets without queryset
            return True
        
        action = self.get_action_from_request(request, view)
        
        # Check permission
        return self.check_user_permission(request.user, model, action)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission for a specific object.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Get the action
        action = self.get_action_from_request(request, view)
        
        # Check model-level permission first
        if not self.check_user_permission(request.user, obj.__class__, action):
            return False
        
        # Check object-level permissions
        return self.check_object_permission(request.user, obj, action)
    
    def get_action_from_request(self, request, view):
        """
        Determine the permission action from the request and view.
        """
        # Get action from view
        if hasattr(view, 'action') and view.action:
            return self.ACTION_MAP.get(view.action, view.action)
        
        # Fallback to HTTP method mapping
        method_map = {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
        }
        return method_map.get(request.method, 'view')
    
    def check_user_permission(self, user, model, action):
        """
        Check if user has permission for a model and action.
        """
        # Create cache key
        cache_key = f"permission_{user.id}_{model._meta.label}_{action}"
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Evaluate permission
        result = self._evaluate_permission(user, model, action)
        
        # Cache result for 5 minutes
        cache.set(cache_key, result, 300)
        
        return result
    
    def _evaluate_permission(self, user, model, action):
        """
        Evaluate permission by checking user roles and permissions.
        """
        try:
            from accounts.models import Permission, UserRole
            
            # Get content type for the model
            content_type = ContentType.objects.get_for_model(model)
            
            # Get user's active roles
            user_roles = UserRole.objects.filter(
                user=user,
                is_active=True
            ).select_related('role')
            
            if not user_roles.exists():
                return False
            
            # Check permissions for each role
            permissions_granted = []
            permissions_denied = []
            
            for user_role in user_roles:
                role = user_role.role
                
                # Get role permissions for this content type and action
                role_permissions = role.rolepermission_set.filter(
                    permission__content_type=content_type,
                    permission__codename__endswith=f'_{action}'
                ).select_related('permission')
                
                for role_permission in role_permissions:
                    if role_permission.granted:
                        permissions_granted.append(role_permission)
                    else:
                        permissions_denied.append(role_permission)
            
            # Apply precedence hierarchy
            return self._resolve_permission_conflicts(permissions_granted, permissions_denied)
            
        except Exception as e:
            logger.error(f"Error evaluating permission for user {user.id}: {e}")
            return False
    
    def _resolve_permission_conflicts(self, granted_permissions, denied_permissions):
        """
        Resolve permission conflicts using precedence hierarchy.
        
        Precedence (highest to lowest):
        1. Explicit deny permissions
        2. Explicit grant permissions
        3. Default deny (no permissions found)
        """
        # If there are explicit deny permissions, deny access
        if denied_permissions:
            return False
        
        # If there are explicit grant permissions, allow access
        if granted_permissions:
            return True
        
        # Default deny
        return False
    
    def check_object_permission(self, user, obj, action):
        """
        Check object-level permissions with additional conditions.
        """
        try:
            from accounts.models import UserRole
            
            # Get user's active roles
            user_roles = UserRole.objects.filter(
                user=user,
                is_active=True
            ).select_related('role')
            
            for user_role in user_roles:
                role = user_role.role
                
                # Get role permissions with conditions
                role_permissions = role.rolepermission_set.filter(
                    permission__content_type=ContentType.objects.get_for_model(obj),
                    permission__codename__endswith=f'_{action}',
                    granted=True
                )
                
                for role_permission in role_permissions:
                    # Check additional conditions
                    if self._check_permission_conditions(user, obj, role_permission.conditions):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking object permission for user {user.id}: {e}")
            return False
    
    def _check_permission_conditions(self, user, obj, conditions):
        """
        Check additional permission conditions.
        
        Conditions can include:
        - Organization/branch restrictions
        - Time-based restrictions
        - Custom business logic
        """
        if not conditions:
            return True
        
        try:
            # Check organization/branch conditions
            if 'sucursal_id' in conditions:
                if hasattr(obj, 'sucursal'):
                    return obj.sucursal.id == conditions['sucursal_id']
                elif hasattr(obj, 'ubicacion') and hasattr(obj.ubicacion, 'acueducto'):
                    return obj.ubicacion.acueducto.sucursal.id == conditions['sucursal_id']
            
            # Check user-specific conditions
            if 'user_id' in conditions:
                return user.id == conditions['user_id']
            
            # Check time-based conditions
            if 'valid_from' in conditions or 'valid_until' in conditions:
                from django.utils import timezone
                now = timezone.now()
                
                if 'valid_from' in conditions:
                    valid_from = timezone.datetime.fromisoformat(conditions['valid_from'])
                    if now < valid_from:
                        return False
                
                if 'valid_until' in conditions:
                    valid_until = timezone.datetime.fromisoformat(conditions['valid_until'])
                    if now > valid_until:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking permission conditions: {e}")
            return False


class PermissionEvaluator:
    """
    Utility class for evaluating permissions outside of DRF views.
    """
    
    @staticmethod
    def user_has_permission(user, model_or_obj, action):
        """
        Check if user has permission for a model/object and action.
        """
        permission_checker = DynamicPermission()
        
        if hasattr(model_or_obj, '_meta'):
            # It's a model class
            return permission_checker.check_user_permission(user, model_or_obj, action)
        else:
            # It's a model instance
            model_permission = permission_checker.check_user_permission(
                user, model_or_obj.__class__, action
            )
            if not model_permission:
                return False
            
            return permission_checker.check_object_permission(user, model_or_obj, action)
    
    @staticmethod
    def get_user_permissions(user, model=None):
        """
        Get all permissions for a user, optionally filtered by model.
        """
        try:
            from accounts.models import UserRole, Permission
            
            # Get user's active roles
            user_roles = UserRole.objects.filter(
                user=user,
                is_active=True
            ).select_related('role')
            
            permissions = []
            
            for user_role in user_roles:
                role = user_role.role
                role_permissions = role.rolepermission_set.select_related('permission')
                
                if model:
                    content_type = ContentType.objects.get_for_model(model)
                    role_permissions = role_permissions.filter(
                        permission__content_type=content_type
                    )
                
                for role_permission in role_permissions:
                    permissions.append({
                        'permission': role_permission.permission,
                        'granted': role_permission.granted,
                        'conditions': role_permission.conditions,
                        'role': role.name
                    })
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    @staticmethod
    def clear_user_permission_cache(user):
        """
        Clear cached permissions for a user.
        """
        # This would need to be implemented based on your cache key pattern
        # For now, we'll clear all cache (not recommended for production)
        cache.clear()


class PermissionMixin:
    """
    Mixin to add permission checking methods to models.
    """
    
    def user_can_view(self, user):
        """Check if user can view this object."""
        return PermissionEvaluator.user_has_permission(user, self, 'view')
    
    def user_can_change(self, user):
        """Check if user can change this object."""
        return PermissionEvaluator.user_has_permission(user, self, 'change')
    
    def user_can_delete(self, user):
        """Check if user can delete this object."""
        return PermissionEvaluator.user_has_permission(user, self, 'delete')