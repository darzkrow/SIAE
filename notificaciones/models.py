from django.db import models
from django.conf import settings

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
