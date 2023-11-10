import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from app.consumers import NotificationConsumer
from django.urls import re_path
# from app.consumers import TestConsumer
from notifications_app.consumers import UserNotificationConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veriprofile.settings')
django.setup()

# Use parentheses to call get_asgi_application
application = get_asgi_application()

import app.routing

application = ProtocolTypeRouter({
    'http': application,
    'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter([
            path("ws/notifications/", NotificationConsumer.as_asgi()),
            re_path(r"ws/usernotification/(?P<room_name>\w+)/$", UserNotificationConsumer.as_asgi()),
        ])))
})
