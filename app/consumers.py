import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("notifications", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def receive(self, text_data):
        # Handle incoming WebSocket messages
        pass

    async def notification(self, event):
        # Send notifications to the WebSocket
        await self.send(json.dumps(event))
