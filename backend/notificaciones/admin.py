from django.contrib import admin
from .models import ConfiguracionTelegram, DestinatarioTelegram

@admin.register(ConfiguracionTelegram)
class ConfiguracionTelegramAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'activo')
    list_editable = ('activo',)

@admin.register(DestinatarioTelegram)
class DestinatarioTelegramAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'chat_id', 'activo')
    list_editable = ('activo',)
    search_fields = ('usuario__username',)
