from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework import generics
from .serializers import UserSerializer, UserUpdateSerializer
from .models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .tokens import create_jwt_pair_for_user

class RegisterView(APIView):
	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_OBJECT,
			required=['username', 'password', 'password2', 'email'],
			properties={
				'username': openapi.Schema(type=openapi.TYPE_STRING, example='example_username'),
				'password': openapi.Schema(type=openapi.TYPE_STRING, example='example_password'),
				'password2': openapi.Schema(type=openapi.TYPE_STRING, example='confirm_password'),
				'email': openapi.Schema(type=openapi.TYPE_STRING, example='example@email.com'),
				'gender': openapi.Schema(
					type=openapi.TYPE_STRING,
					enum=['M', 'F', 'N'],
					example='M'
				),
				'phone': openapi.Schema(type=openapi.TYPE_STRING, example='87988553300')
			},
		),
	)
	def post(self, request):
		serializer = UserSerializer(data=request.data)
		try:
			serializer.is_valid(raise_exception=True)
			serializer.save()
			return Response(serializer.data)
		except ValidationError as e:
			return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_OBJECT,
			required=['username', 'password'],
			properties={
				'username': openapi.Schema(type=openapi.TYPE_STRING, example='example_username'),
				'password': openapi.Schema(type=openapi.TYPE_STRING, example='example_password'),
			},
		),
	)
	def post(self, request):
		username = request.data.get('username')
		password = request.data.get('password')

		user = User.objects.filter(username=username).first()

		if user is None:
			raise AuthenticationFailed('Usuário não encontrado!')
		
		if not user.check_password(password):
			raise AuthenticationFailed('A senha está incorreta!')
		
		tokens = create_jwt_pair_for_user(user)

		return JsonResponse({
			"message": 'Login realizado com sucesso!',
			'tokens': tokens
		})
	
class UserDetailView(APIView):
	def delete(self, request, user_id):
		user = get_object_or_404(User, id=user_id)
		user.delete()
		return JsonResponse({
			"message": 'Usuário removido com sucesso!',
		})

	@swagger_auto_schema(
		request_body=openapi.Schema(
			type=openapi.TYPE_OBJECT,
			required=['username', 'password', '', 'email'],
			properties={
				'username': openapi.Schema(type=openapi.TYPE_STRING, example='example_username'),
				'password': openapi.Schema(type=openapi.TYPE_STRING, example='example_password'),
				'email': openapi.Schema(type=openapi.TYPE_STRING, example='example@email.com'),
				'gender': openapi.Schema(
					type=openapi.TYPE_STRING,
					enum=['M', 'F', 'N'],
					example='M'
				),
				'phone': openapi.Schema(type=openapi.TYPE_STRING, example='87988553300')
			},
		),
	)
	def patch(self, request, user_id):
		user = get_object_or_404(User, id=user_id)
		serializer = UserUpdateSerializer(user, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)