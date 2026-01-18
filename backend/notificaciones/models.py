from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from institucion.models import Acueducto

class ConfiguracionTelegram(models.Model):
    """
    Modelo para almacenar la configuración del bot de Telegram.
    Se usa un único registro (Singleton) para la configuración global.
    """
    bot_token = models.CharField(max_length=200, help_text="Token del Bot de Telegram.")
    activo = models.BooleanField(default=True, help_text="Activar/desactivar globalmente las notificaciones a Telegram.")

    def __str__(self):
        return "Configuración de Telegram"

    class Meta:
        verbose_name = "Configuración de Telegram"
        verbose_name_plural = "Configuraciones de Telegram"

    def save(self, *args, **kwargs):
        # Asegurar que solo exista una instancia de este modelo
        self.pk = 1
        super(ConfiguracionTelegram, self).save(*args, **kwargs)

class DestinatarioTelegram(models.Model):
    """
    Asocia un usuario del sistema con su ID de chat de Telegram.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='destinatario_telegram'
    )
    chat_id = models.CharField(max_length=100, unique=True, help_text="ID del chat de Telegram del usuario.")
    activo = models.BooleanField(default=True, help_text="El usuario desea recibir notificaciones en Telegram.")

    def __str__(self):
        return f"{self.usuario.username} ({self.chat_id})"

    class Meta:
        verbose_name = "Destinatario de Telegram"
        verbose_name_plural = "Destinatarios de Telegram"

class Alerta(models.Model):
    """Configuración de alertas de stock bajo."""
    # Relación Genérica al Producto
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    
    acueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    umbral_minimo = models.DecimalField(max_digits=12, decimal_places=3)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Alerta de Stock'
        verbose_name_plural = 'Alertas de Stock'
        unique_together = ['content_type', 'object_id', 'acueducto']

    def __str__(self):
        return f"Alerta {self.producto} - {self.acueducto} (< {self.umbral_minimo})"


class Notificacion(models.Model):
    """Notificaciones generadas por el sistema."""
    mensaje = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, default='INFO')  # INFO, WARNING, CRITICAL
    leida = models.BooleanField(default=False)
    enviada = models.BooleanField(default=False)  # Para emails/externos
    creada_en = models.DateTimeField(auto_now_add=True)
    
    # Opcional: Relacionar con usuario si es específica
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creada_en']

    def __str__(self):
        return f"{self.mensaje} ({self.creada_en})"
