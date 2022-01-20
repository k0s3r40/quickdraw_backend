from django.urls import re_path

from quickdraw_backend.consumers import MultiplayerHandler

websocket_urlpatterns = [
    re_path(r'ws/socket-server/', MultiplayerHandler.as_asgi())
]