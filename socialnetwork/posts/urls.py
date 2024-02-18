from django.urls import path, include
from .views import *

app_name = 'posts'

urlpatterns = [
	path('tela', postPage2, name="chat-page"),
	path('', PostViewsets.as_view({
		'get': 'index',
		'post': 'create',
	})),
	path('friends/', PostViewsets.as_view({
		'get': 'friends_posts'
	}), name="friends-posts"),
	path('<uuid:pk>/', PostViewsets.as_view({
		'get': 'retrieve',
		'put': 'update',
		'delete': 'destroy',
	})),
	path('<uuid:pk>/like/', PostViewsets.as_view({
		'post': 'like_post',
		'delete': 'unlike_post',
	})),
	path('<uuid:post_id>/comments/', CommentViewSet.as_view({
		'get': 'list',
		'post': 'create',
	})),
	path('<uuid:post_id>/comments/<uuid:pk>/', CommentViewSet.as_view({
		'put': 'update',
		'delete': 'destroy',
	})),
]
