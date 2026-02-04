from .models import AuditLog
from .middleware import get_current_request_data
from django.contrib.contenttypes.models import ContentType

def log_action(instance, action, changes=None, risk_level='LOW', extra_data=None):
    """
    Registra una acción en el log de auditoría.
    
    Args:
        instance: Instancia del objeto afectado
        action: Tipo de acción (debe estar en AuditLog.ACTION_CHOICES)
        changes: Diccionario con los cambios realizados
        risk_level: Nivel de riesgo de la acción
        extra_data: Datos adicionales específicos del contexto
    """
    request_data = get_current_request_data()
    user = request_data.get('user')
    
    # Fallback si no hay usuario en local thread (ej: tests or system actions)
    if not user and hasattr(instance, 'creado_por'):
        user = instance.creado_por

    # Solo loguear si el usuario está autenticado (o si queremos loguear acciones del sistema)
    if user and not user.is_authenticated:
        user = None

    # Use the enhanced log_action class method
    return AuditLog.log_action(
        user=user,
        action=action,
        content_object=instance,
        changes=changes,
        ip_address=request_data.get('ip'),
        user_agent=request_data.get('user_agent'),
        session_key=request_data.get('session_key'),
        extra_data=extra_data,
        risk_level=risk_level
    )

def log_authentication_action(user, action, success=True, ip_address=None, 
                            user_agent=None, extra_data=None):
    """
    Registra acciones de autenticación (login, logout, etc.).
    
    Args:
        user: Usuario involucrado en la acción
        action: Tipo de acción de autenticación
        success: Si la acción fue exitosa
        ip_address: Dirección IP
        user_agent: User agent del navegador
        extra_data: Datos adicionales
    """
    risk_level = 'MEDIUM' if not success else 'LOW'
    
    # For failed login attempts, we might not have a user object
    if not success and not user:
        user = None
        extra_data = extra_data or {}
        extra_data['attempted_username'] = extra_data.get('username', 'unknown')
    
    return AuditLog.log_action(
        user=user,
        action=action,
        content_object=user if user else None,
        changes={'success': success},
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=extra_data,
        risk_level=risk_level
    )

def log_permission_action(user, action, target_user=None, permission=None, 
                         role=None, granted=True, ip_address=None, 
                         user_agent=None, extra_data=None):
    """
    Registra acciones relacionadas con permisos y roles.
    
    Args:
        user: Usuario que realiza la acción
        action: Tipo de acción (PERMISSION_GRANT, ROLE_ASSIGN, etc.)
        target_user: Usuario afectado por el cambio de permisos
        permission: Permiso involucrado
        role: Rol involucrado
        granted: Si el permiso/rol fue concedido o revocado
        ip_address: Dirección IP
        user_agent: User agent del navegador
        extra_data: Datos adicionales
    """
    changes = {'granted': granted}
    content_object = target_user
    object_repr = f"Usuario: {target_user.username}" if target_user else "N/A"
    
    if permission:
        changes['permission'] = str(permission)
        object_repr += f" - Permiso: {permission}"
    
    if role:
        changes['role'] = str(role)
        object_repr += f" - Rol: {role}"
    
    extra_data = extra_data or {}
    if permission:
        extra_data['permission_id'] = permission.id
    if role:
        extra_data['role_id'] = role.id
    
    return AuditLog.log_action(
        user=user,
        action=action,
        content_object=content_object,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=extra_data,
        risk_level='HIGH'  # Permission changes are high risk
    )

def log_configuration_change(user, config_key, old_value, new_value, 
                           ip_address=None, user_agent=None, extra_data=None):
    """
    Registra cambios en la configuración del sistema.
    
    Args:
        user: Usuario que realizó el cambio
        config_key: Clave de configuración modificada
        old_value: Valor anterior
        new_value: Nuevo valor
        ip_address: Dirección IP
        user_agent: User agent del navegador
        extra_data: Datos adicionales
    """
    changes = {
        'config_key': config_key,
        'old_value': old_value,
        'new_value': new_value
    }
    
    extra_data = extra_data or {}
    extra_data['config_key'] = config_key
    
    return AuditLog.log_action(
        user=user,
        action='CONFIG_CHANGE',
        content_object=None,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=extra_data,
        risk_level='MEDIUM'
    )

def log_data_operation(user, action, affected_count=0, operation_type=None,
                      ip_address=None, user_agent=None, extra_data=None):
    """
    Registra operaciones masivas de datos (import, export, bulk operations).
    
    Args:
        user: Usuario que realizó la operación
        action: Tipo de acción (EXPORT, IMPORT, BULK_UPDATE, etc.)
        affected_count: Número de registros afectados
        operation_type: Tipo específico de operación
        ip_address: Dirección IP
        user_agent: User agent del navegador
        extra_data: Datos adicionales
    """
    changes = {
        'affected_count': affected_count,
        'operation_type': operation_type
    }
    
    extra_data = extra_data or {}
    extra_data['affected_count'] = affected_count
    if operation_type:
        extra_data['operation_type'] = operation_type
    
    # Determine risk level based on affected count
    if affected_count > 1000:
        risk_level = 'HIGH'
    elif affected_count > 100:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    return AuditLog.log_action(
        user=user,
        action=action,
        content_object=None,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=extra_data,
        risk_level=risk_level
    )

def log_access_denied(user, resource, reason=None, ip_address=None, 
                     user_agent=None, extra_data=None):
    """
    Registra intentos de acceso denegado para monitoreo de seguridad.
    
    Args:
        user: Usuario que intentó el acceso (puede ser None)
        resource: Recurso al que se intentó acceder
        reason: Razón del acceso denegado
        ip_address: Dirección IP
        user_agent: User agent del navegador
        extra_data: Datos adicionales
    """
    changes = {
        'resource': str(resource),
        'reason': reason or 'Permisos insuficientes'
    }
    
    extra_data = extra_data or {}
    extra_data['resource'] = str(resource)
    extra_data['reason'] = reason
    
    return AuditLog.log_action(
        user=user,
        action='ACCESS_DENIED',
        content_object=None,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=extra_data,
        risk_level='MEDIUM'
    )
