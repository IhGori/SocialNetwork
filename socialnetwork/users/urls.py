from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
	path('register', RegisterView.as_view(), name='register'),
	path('login', LoginView.as_view(), name='login'),
	path('<str:user_id>', UserDetailView.as_view(), name='user-detail'),
]