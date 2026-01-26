from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

class SoftDeleteManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeleteQuerySet(self.model).filter(deleted_at__isnull=True)
        return SoftDeleteQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True)
    
    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        super(SoftDeleteModel, self).delete()


class AuditLog(models.Model):
    """
    Comprehensive audit logging model for tracking all system activities.
    
    This model provides complete audit trail functionality including:
    - User actions (CRUD operations, authentication)
    - Permission modifications
    - Configuration changes
    - System activities
    
    Requirements: 3.4, 5.6, 8.3
    """
    ACTION_CHOICES = [
        # CRUD Operations
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación (Soft)'),
        ('RESTORE', 'Restauración'),
        ('HARD_DELETE', 'Eliminación Física'),
        
        # Authentication Actions
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('LOGIN_FAILED', 'Intento de Inicio de Sesión Fallido'),
        ('PASSWORD_CHANGE', 'Cambio de Contraseña'),
        ('PASSWORD_RESET', 'Restablecimiento de Contraseña'),
        
        # Permission Actions
        ('PERMISSION_GRANT', 'Concesión de Permiso'),
        ('PERMISSION_REVOKE', 'Revocación de Permiso'),
        ('ROLE_ASSIGN', 'Asignación de Rol'),
        ('ROLE_REMOVE', 'Eliminación de Rol'),
        
        # Configuration Actions
        ('CONFIG_CHANGE', 'Cambio de Configuración'),
        ('SYSTEM_MAINTENANCE', 'Mantenimiento del Sistema'),
        
        # Data Operations
        ('EXPORT', 'Exportación de Datos'),
        ('IMPORT', 'Importación de Datos'),
        ('BULK_UPDATE', 'Actualización Masiva'),
        ('BULK_DELETE', 'Eliminación Masiva'),
        
        # Access Control
        ('ACCESS_DENIED', 'Acceso Denegado'),
        ('UNAUTHORIZED_ACCESS', 'Intento de Acceso No Autorizado'),
    ]

    # User who performed the action (null for system actions)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="Usuario que realizó la acción (nulo para acciones del sistema)"
    )
    
    # Action performed
    action = models.CharField(
        max_length=30, 
        choices=ACTION_CHOICES,
        help_text="Tipo de acción realizada"
    )
    
    # Generic relation to the object being acted upon
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        help_text="Tipo de contenido del objeto afectado"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID del objeto afectado"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # String representation of the affected object
    object_repr = models.CharField(
        max_length=255, 
        help_text="Representación textual del objeto afectado"
    )
    
    # Detailed changes made (JSON format for structured data)
    changes = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Detalles de los cambios realizados en formato JSON"
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="Dirección IP desde donde se realizó la acción"
    )
    user_agent = models.TextField(
        null=True, 
        blank=True,
        help_text="User agent del navegador/cliente"
    )
    
    # Additional request context
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        help_text="Clave de sesión asociada"
    )
    
    # Timing information
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Momento en que se realizó la acción"
    )
    
    # Additional metadata
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales específicos del contexto"
    )
    
    # Risk level for security monitoring
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
        ('CRITICAL', 'Crítico'),
    ]
    
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default='LOW',
        help_text="Nivel de riesgo de la acción para monitoreo de seguridad"
    )

    class Meta:
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['risk_level', 'timestamp']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'Sistema'
        return f"{user_str} - {self.get_action_display()} - {self.object_repr} ({self.timestamp})"
    
    def get_changes_summary(self):
        """
        Get a human-readable summary of changes made.
        
        Returns:
            str: Summary of changes or empty string if no changes
        """
        if not self.changes:
            return ""
        
        if isinstance(self.changes, dict):
            if 'fields_changed' in self.changes:
                fields = ', '.join(self.changes['fields_changed'])
                return f"Campos modificados: {fields}"
            elif 'old_values' in self.changes and 'new_values' in self.changes:
                changed_fields = []
                for field, old_val in self.changes.get('old_values', {}).items():
                    new_val = self.changes.get('new_values', {}).get(field)
                    changed_fields.append(f"{field}: {old_val} → {new_val}")
                return "; ".join(changed_fields)
        
        return str(self.changes)
    
    @classmethod
    def log_action(cls, user, action, content_object=None, changes=None, 
                   ip_address=None, user_agent=None, session_key=None, 
                   extra_data=None, risk_level='LOW'):
        """
        Convenience method to create audit log entries.
        
        Args:
            user: User who performed the action (can be None for system actions)
            action: Action type (must be one of ACTION_CHOICES)
            content_object: Object that was acted upon (optional)
            changes: Dictionary of changes made (optional)
            ip_address: IP address of the request (optional)
            user_agent: User agent string (optional)
            session_key: Session key (optional)
            extra_data: Additional context data (optional)
            risk_level: Risk level of the action (default: 'LOW')
            
        Returns:
            AuditLog: Created audit log instance
        """
        content_type = None
        object_id = None
        object_repr = "N/A"
        
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = content_object.pk
            object_repr = str(content_object)[:255]
        
        return cls.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            extra_data=extra_data or {},
            risk_level=risk_level
        )
