from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from users.models import User
import uuid


def index(request):
	return render(request, "chat/index.html")


def room(request, room_name):
	return render(request, "chat/room.html", {"room_name": room_name})

class GenerateChatChannelAPIView(APIView):
	def post(self, request):
		# Obtenha o ID do usuário que está enviando a solicitação e o ID do usuário com quem ele quer conversar
		sender_id = request.data.get('sender_id')
		receiver_id = request.data.get('receiver_id')

		# Verifique se os IDs fornecidos correspondem a usuários existentes
		sender = User.objects.filter(id=sender_id).first()
		receiver = User.objects.filter(id=receiver_id).first()

		if sender and receiver:
			# Verifique se o usuário que envia a solicitação é amigo do usuário com quem deseja conversar
			if receiver in sender.friends.all():
				# Converta os IDs para string e ordene-os alfabeticamente
				sender_id_str = str(uuid.UUID(sender_id))
				receiver_id_str = str(uuid.UUID(receiver_id))
				sorted_ids = sorted([sender_id_str, receiver_id_str])

				# Crie um identificador único para o canal
				channel_id = '-'.join(sorted_ids)
				
				# Retorne o identificador do canal como resposta à solicitação
				return Response({'channel_id': channel_id}, status=status.HTTP_200_OK)
			else:
				return Response({'error': 'Você não é amigo desse usuário.'}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({'error': 'IDs de usuário inválidos.'}, status=status.HTTP_400_BAD_REQUEST)