from django.urls import path, include
from .views import *

app_name = 'posts'

urlpatterns = [
	path("posts/tela", postPage, name="chat-page"),
	path('posts/', PostViewsets.as_view({
		'get': 'index',
		'post': 'create',
	})),
	path('posts/<uuid:pk>/', PostViewsets.as_view({
		'get': 'retrieve',
		'put': 'update',
		'delete': 'destroy',
	})),
	path('posts/<uuid:pk>/like/', PostViewsets.as_view({
		'post': 'like_post',
		'delete': 'unlike_post',
		})),
]