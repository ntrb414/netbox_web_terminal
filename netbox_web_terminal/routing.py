from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/terminal/<int:pk>/', consumers.TerminalConsumer.as_view()),
]
