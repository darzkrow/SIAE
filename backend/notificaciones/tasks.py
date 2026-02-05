from celery import shared_task
import requests
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def send_telegram_notification(message, chat_id=None):
    """
    Tarea asíncrona para enviar notificaciones a Telegram.
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    # Si no se pasa chat_id, usar el por defecto
    if not chat_id:
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
        except Exception as e:
            print(f"Error enviando notificación a Telegram: {e}")

@shared_task
def broadcast_notification(payload, group_name='notifications_global', user_id=None):
    """
    Tarea para enviar notificación via WebSockets (Channels).
    Si user_id está presente, apunta al grupo específico del usuario.
    """
    channel_layer = get_channel_layer()
    
    target_group = f'user_{user_id}' if user_id else group_name
    
    async_to_sync(channel_layer.group_send)(
        target_group,
        {
            'type': 'send_notification',
            'payload': payload
        }
    )
