import json
import time
import uuid
from threading import Thread
from time import sleep

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
        self.send(json.dumps({'type': 'creds', 'message': self.user_id, 'room_id': self.room.name}))
        if self.room.can_start:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': 'The battle is about to start'
                }
            )

            self.x = Thread(target=self.start_battle, args=(4,))
            self.x.start()

    def receive(self, text_data=None, bytes_data=None):
        if json.loads(text_data)['message'] == "S":
            if self.x.is_alive() is False:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': json.loads(text_data)['user_id'] + ' Has won the game'
                    }
                )
            else:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': json.loads(text_data)['user_id'] + ' Has shot prematurely and Lost the game'
                    }
                )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({'type': 'data', 'message': message}))

    def start_battle(self, secs):
        for i in range(secs):
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': i
                }
            )
            time.sleep(1)
