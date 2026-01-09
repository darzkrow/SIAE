from rest_framework import permissions
from accounts.models import CustomUser


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso que solo permite escritura a administradores.
    Operadores solo pueden leer.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lectura permitida para todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para administradores
        return request.user.role == CustomUser.ROLE_ADMIN


class IsAdminOrSameSucursal(permissions.BasePermission):
    """
    Permiso que permite a administradores ver todo,
    pero operadores solo pueden ver datos de su sucursal.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Administradores pueden ver todo
        if request.user.role == CustomUser.ROLE_ADMIN:
            return True
        
        # Operadores solo pueden ver objetos de su sucursal
        if request.user.sucursal is None:
            return False
        
        # Verificar según el tipo de objeto
        if hasattr(obj, 'sucursal'):
            return obj.sucursal == request.user.sucursal
        elif hasattr(obj, 'acueducto') and hasattr(obj.acueducto, 'sucursal'):
            return obj.acueducto.sucursal == request.user.sucursal
        elif hasattr(obj, 'acueducto_origen') or hasattr(obj, 'acueducto_destino'):
            # Para movimientos, verificar que al menos uno de los acueductos pertenezca a la sucursal
            origen_ok = (obj.acueducto_origen and 
                        obj.acueducto_origen.sucursal == request.user.sucursal)
            destino_ok = (obj.acueducto_destino and 
                         obj.acueducto_destino.sucursal == request.user.sucursal)
            return origen_ok or destino_ok
        
        # Por defecto, permitir acceso
        return True


class CanApproveMovements(permissions.BasePermission):
    """
    Permiso para aprobar movimientos críticos.
    Solo administradores pueden aprobar.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == CustomUser.ROLE_ADMIN


class CanManageUsers(permissions.BasePermission):
    """
    Permiso para gestionar usuarios.
    Solo administradores pueden gestionar usuarios.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == CustomUser.ROLE_ADMIN