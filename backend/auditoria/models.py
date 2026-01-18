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
    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación (Soft)'),
        ('RESTORE', 'Restauración'),
        ('HARD_DELETE', 'Eliminación Física'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Generic relation to the object being acted upon
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    object_repr = models.CharField(max_length=255, help_text="Representación textual del objeto")
    changes = models.JSONField(null=True, blank=True, help_text="Descripción de los cambios realizados")
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_repr} ({self.timestamp})"
