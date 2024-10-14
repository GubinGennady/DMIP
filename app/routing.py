from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws', consumers.YourConsumer.as_asgi()),
    path('google', consumers.WSGoogle.as_asgi()),
    path('mail', consumers.WSMail.as_asgi()),
]
