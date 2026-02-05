from rest_framework.permissions import BasePermission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class IsAdminOrReadOnly(BasePermission):
    """Permiso que solo permite escritura a administradores. Operadores solo pueden leer."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated: return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'): return True
        return hasattr(request.user, 'role') and request.user.role == 'ADMIN'

class IsAdminOrSameSucursal(BasePermission):
    """Permiso que permite a administradores ver todo, pero operadores solo ven su sucursal."""
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN': return True
        if not request.user.sucursal: return False
        
        if hasattr(obj, 'sucursal'): return obj.sucursal == request.user.sucursal
        if hasattr(obj, 'ubicacion'):
            u = obj.ubicacion
            if not u: return True
            if u.subalmacen: return u.subalmacen.sucursal == request.user.sucursal
            if u.almacen_regional: return u.almacen_regional.sucursal == request.user.sucursal
            if u.acueducto: return u.acueducto.sucursal == request.user.sucursal
        return True

class CanApproveMovements(BasePermission):
    """Permiso para aprobar movimientos críticos. Solo administradores pueden aprobar."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'ADMIN'

class CanManageUsers(BasePermission):
    """Permiso para gestionar usuarios. Solo administradores pueden gestionar usuarios."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'ADMIN'

class DynamicPermission(BasePermission):
    """
    Dynamic permission class that evaluates permissions from database.
    """
    ACTION_MAP = {
        'list': 'view',
        'retrieve': 'view',
        'create': 'add',
        'update': 'change',
        'partial_update': 'change',
        'destroy': 'delete',
    }
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
            
        model = getattr(view, 'queryset', None)
        if model is not None:
            model = model.model
        else:
            return True
            
        action = self.get_action_from_request(request, view)
        return self.check_user_permission(request.user, model, action)

    def get_action_from_request(self, request, view):
        if hasattr(view, 'action') and view.action:
            return self.ACTION_MAP.get(view.action, view.action)
        method_map = {'GET': 'view', 'POST': 'add', 'PUT': 'change', 'PATCH': 'change', 'DELETE': 'delete'}
        return method_map.get(request.method, 'view')

    def check_user_permission(self, user, model, action):
        cache_key = f"perm_{user.id}_{model._meta.label}_{action}"
        result = cache.get(cache_key)
        if result is not None:
            return result
        
        result = self._evaluate_permission(user, model, action)
        cache.set(cache_key, result, 300)
        return result

    def _evaluate_permission(self, user, model, action):
        # Admin bypass role checking
        if hasattr(user, 'role') and user.role == 'ADMIN':
            return True
        return False # Default for now, implementation depends on accounts app logic
