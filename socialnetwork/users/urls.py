from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
	path('user/register', RegisterView.as_view()),
	path('user/login', LoginView.as_view()),
	path('user/<str:user_id>', UserDetailView.as_view()),
]