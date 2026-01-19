from .models import AuditLog
from .middleware import get_current_request_data
from django.contrib.contenttypes.models import ContentType

def log_action(instance, action, changes=None):
    """
    Registra una acción en el log de auditoría.
    """
    request_data = get_current_request_data()
    user = request_data.get('user')
    
    # Fallback si no hay usuario en local thread (ej: tests or system actions)
    if not user and hasattr(instance, 'creado_por'):
        user = instance.creado_por

    # Solo loguear si el usuario está autenticado (o si queremos loguear acciones del sistema)
    if user and not user.is_authenticated:
        user = None

    ct = ContentType.objects.get_for_model(instance)
    
    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=ct,
        object_id=instance.pk,
        object_repr=str(instance)[:255],
        changes=changes,
        ip_address=request_data.get('ip'),
        user_agent=request_data.get('user_agent')
    )
