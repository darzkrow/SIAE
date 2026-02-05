import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        # Grupos: uno global y uno específico para el usuario
        self.global_group = 'notifications_global'
        self.user_group = f'user_{user.id}'
        
        # Unirse a ambos grupos
        await self.channel_layer.group_add(self.global_group, self.channel_name)
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'global_group'):
            await self.channel_layer.group_discard(self.global_group, self.channel_name)
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def send_notification(self, event):
        """
        Handler para enviar notificaciones al cliente.
        Se espera un 'payload' estructurado.
        """
        await self.send(text_data=json.dumps(event['payload']))
