import json
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from datetime import datetime

from rooms.models import Room
from django.db.models import Q


class MultiplayerHandler(WebsocketConsumer):
    def connect(self):
        self.room = Room.objects.filter(Q(p_1=None) | Q(p_2=None))
        if self.room.exists():
            self.room = self.room.first()
        else:
            self.room = Room.objects.create()
        self.room_group_name = self.room.name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.user_id = str(uuid.uuid4())
        if self.room.p_1 is None:
            self.room.p_1 = self.user_id
        else:
            self.room.p_2 = self.user_id
        self.room.save()
        self.send(json.dumps({'type':'creds','message': self.user_id, 'room_id':self.room.name}))

    def receive(self, text_data=None, bytes_data=None):

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({'type':'data','message':message }))
