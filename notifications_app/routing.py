# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/usernotification/(?P<room_name>\w+)/$", consumers.UserNotificationConsumer.as_asgi()),
]