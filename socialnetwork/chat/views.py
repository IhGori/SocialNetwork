from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from .serializers import *
from users.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer
from django.db.models import Q
from django.http import JsonResponse
from users.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from cryptography.fernet import Fernet
import secrets

class ConversationsListAPIView(APIView):
	def get(self, request):
		user_id = request.query_params.get('user')
		user = get_object_or_404(User, id=user_id)   
		user_messages = Message.objects.filter(Q(sender=user) | Q(receiver=user))
		messages_serializer = MessageSerializer(user_messages, many=True)
		serialized_data = messages_serializer.data
		return JsonResponse({
			"message": f"Lista das conversas relacionadas com o usuário {user.username}",
			"data": serialized_data
		})

class MessageListByConversation(APIView):
	serializer_class = MessageSerializer
	def get(self, request):
		conversation_id = self.request.query_params.get('conversation')
		conversation = get_object_or_404(Conversation, channel_id=conversation_id)
		messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
		serializer = MessageSerializer(messages, many=True)
		return Response(serializer.data)



class GenerateChatChannelAPIView(APIView):
	def post(self, request):
		sender_id = request.data.get('sender_id')
		receiver_id = request.data.get('receiver_id')

		sender = User.objects.filter(id=sender_id).first()
		receiver = User.objects.filter(id=receiver_id).first()

		if sender and receiver:
			if receiver in sender.friends.all():
				sender_id_str = str(uuid.UUID(sender_id))
				receiver_id_str = str(uuid.UUID(receiver_id))
				sorted_ids = sorted([str(uuid.UUID(sender_id)), str(uuid.UUID(receiver_id))])
				channel_id = '-'.join(sorted_ids)

				conversation = Conversation.objects.filter(channel_id=channel_id).first()
				if not conversation:
					conversation = Conversation.objects.create(channel_id=channel_id)

				return Response({'channel_id': channel_id}, status=status.HTTP_200_OK)
			else:
				return Response({'error': 'Você não é amigo desse usuário.'}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({'error': 'IDs de usuário inválidos.'}, status=status.HTTP_400_BAD_REQUEST)

class CreateMessageAPIView(APIView):
	JWT_authenticator = JWTAuthentication()

	def post(self, request, channel_id):
		response = self.JWT_authenticator.authenticate(request)

		if response is not None:
			user, token = response
			
			data = request.data
			text = data.get('text')
			receiver_id = data.get('receiver')

			sender_user = get_object_or_404(User, pk=user.id)
			receiver_user = get_object_or_404(User, pk=receiver_id)

			try:
				conversation = Conversation.objects.get(channel_id=channel_id)
			except Conversation.DoesNotExist:
				conversation = Conversation.objects.create(channel_id=channel_id)

			message = Message.objects.create(
				conversation=conversation,
				sender=sender_user,
				receiver=receiver_user,
				text=text
			)

			serializer = MessageSerializer(message)

			return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)