
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import app.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack



application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                app.routing.websocket_urlpatterns
            )
        )
    }
)