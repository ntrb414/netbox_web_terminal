from django.urls import path
from . import views

urlpatterns = [
    path('device/<int:pk>/', views.DeviceTerminalView.as_view(), name='device_terminal'),
]
