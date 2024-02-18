from django.urls import path

from . import views
from .views import *


urlpatterns = [
	path("", views.index, name="index"),
	path("<str:room_name>/", views.room, name="room"),
    path('api/generate_chat_channel/', GenerateChatChannelAPIView.as_view(), name='generate_chat_channel'),
]