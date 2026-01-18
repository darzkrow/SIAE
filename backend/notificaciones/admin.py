from django.contrib import admin
from .models import Notificacion, Alerta, ConfiguracionTelegram, DestinatarioTelegram

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['mensaje', 'tipo', 'leida', 'creada_en']
    list_filter = ['tipo', 'leida']

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'acueducto', 'umbral_minimo', 'activo']
    list_filter = ['activo']

@admin.register(ConfiguracionTelegram)
class ConfiguracionTelegramAdmin(admin.ModelAdmin):
    list_display = ['bot_token', 'activo']

@admin.register(DestinatarioTelegram)
class DestinatarioTelegramAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'chat_id', 'activo']
