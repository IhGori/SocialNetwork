from django.urls import path
from .views import *

app_name = 'chat'

urlpatterns = [
	path('conversations/', ConversationsListAPIView.as_view()),
	path('messages/', MessageListByConversation.as_view()),
	path('generate-channel/', GenerateChatChannelAPIView.as_view()),
	path('<str:channel_id>/', CreateMessageAPIView.as_view()),
]