import json
from channels.generic.websocket import AsyncWebSocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebSocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        user = self.scope['user']

        if user.is_anonymous:
            await self.close()
            return

        is_participant = await self.check_participant(user, self.room_id)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = await self.save_message(
                self.scope['user'],
                self.room_id,
                data['message'],
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'sender_id': self.scope['user'].id,
                    'sender_name': self.scope['user'].username,
                    'timestamp': message.created_at.isoformat(),
                    'message_id': message.id,
                },
            )
        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'sender_id': self.scope['user'].id,
                    'sender_name': self.scope['user'].username,
                },
            )
        elif message_type == 'mark_read':
            await self.mark_messages_read(self.scope['user'], self.room_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'reader_id': self.scope['user'].id,
                },
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    async def typing_indicator(self, event):
        if event['sender_id'] != self.scope['user'].id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'sender_name': event['sender_name'],
            }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'reader_id': event['reader_id'],
        }))

    @database_sync_to_async
    def check_participant(self, user, room_id):
        from .models import ChatRoom
        try:
            room = ChatRoom.objects.select_related(
                'application__applicant', 'application__job__company',
            ).get(id=room_id)
            return user in [room.application.applicant, room.application.job.company]
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        from .models import ChatRoom, Message
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=user, content=content)

    @database_sync_to_async
    def mark_messages_read(self, user, room_id):
        from .models import Message
        Message.objects.filter(
            room_id=room_id, is_read=False,
        ).exclude(sender=user).update(is_read=True)
