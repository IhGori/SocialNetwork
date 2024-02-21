from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
	path('register', RegisterView.as_view(), name='register'),
	path('login', LoginView.as_view(), name='login'),
	path('<str:user_id>', UserDetailView.as_view(), name='user-detail'),
	path('<str:friend_id>/add-friend/', AddFriendView.as_view()),
	path('<str:friend_id>/remove-friend/', RemoveFriendView.as_view()),
]