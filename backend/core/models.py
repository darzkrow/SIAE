from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    🕐 Modelo con Timestamps Automáticos    
    Agrega automáticamente fechas de creación y actualización.
    ¡Como un reloj que guarda cuándo hiciste algo!
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Cuándo se creó este registro"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Última vez que se modificó"
    )

    class Meta:
        abstract = True  # Este modelo no crea tabla, solo se hereda


class SoftDeleteManager(models.Manager):
    """
    🗑️ Manager para Soft Deletes    
    Solo muestra registros que no están eliminados.
    ¡Como tener una papelera de reciclaje!
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(TimeStampedModel):
    """
    🗑️ Modelo con Eliminación Suave (Soft Delete)    
    En lugar de borrar de verdad, solo marca como eliminado.
    ¡Puedes recuperar cosas de la papelera!
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Eliminación",
        help_text="Cuándo se eliminó (null = no eliminado)"
    )

    objects = SoftDeleteManager()  # Manager por defecto (sin eliminados)
    all_objects = models.Manager()  # Manager para ver todo (incluye eliminados)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Eliminar suavemente (marcar como eliminado)"""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaurar un registro eliminado"""
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        """¿Está eliminado?"""
        return self.deleted_at is not None


class BaseModel(SoftDeleteModel):
    """
    🏗️ Modelo Base Completo    
    Combina timestamps y soft deletes.
    ¡El modelo más completo para heredar!
    """
    class Meta:
        abstract = True
        ordering = ['-created_at']  # Más recientes primero

    def __str__(self):
        """Representación en texto del modelo"""
        if hasattr(self, 'name'):
            return self.name
        elif hasattr(self, 'nombre'):
            return self.nombre
        return f"{self.__class__.__name__} #{self.pk}"
class SystemConfiguration(models.Model):
    """Configuración global del sistema."""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventario_systemconfiguration'
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'

    def __str__(self):
        return self.key
