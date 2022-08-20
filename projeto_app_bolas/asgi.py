"""
ASGI config for projeto_app_bolas project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

from operator import index
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import appBolas.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_app_bolas.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            appBolas.routing.websocket_urlpatterns
        )
    )

})
