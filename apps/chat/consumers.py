# apps/chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Message, Conversation

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Ստանալ conversation_id URL-ից
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        if not message_text:
            return  # դատարկ message ուղարկելու թույլ չտալ

        sender = self.scope["user"]

        # Ստանալ Conversation DB-ից async-safe
        try:
            conversation = await sync_to_async(Conversation.objects.get)(id=self.conversation_id)
        except Conversation.DoesNotExist:
            return  # եթե conversation չկա

        # Ստուգել, որ sender-ը conversation-ի անդամ է
        if not await sync_to_async(lambda: sender in [conversation.user1, conversation.user2])():
            return  # ոչ թույլատրված

        # Ստեղծել Message DB-ում async-safe
        await sync_to_async(Message.objects.create)(
            conversation=conversation,
            sender=sender,
            text=message_text
        )

        # Ուղարկել message-ին բոլոր connected users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': sender.id
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message_text = event['message']
        sender_id = event['sender_id']

        # Ուղարկել message WebSocket-ին
        await self.send(text_data=json.dumps({
            'message': message_text,
            'sender_id': sender_id
        }))
