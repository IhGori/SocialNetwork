from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
	path('register', RegisterView.as_view()),
	path('login', LoginView.as_view()),
	path('<str:user_id>', UserDetailView.as_view()),
]