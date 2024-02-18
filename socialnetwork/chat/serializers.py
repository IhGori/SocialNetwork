from rest_framework import serializers
from .models import Conversation, Message
from users.models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'username']

class MessageSerializer(serializers.ModelSerializer):
	sender = UserSerializer(read_only=True)
	receiver = UserSerializer(read_only=True)

	class Meta:
		model = Message
		fields = ['id', 'sender', 'receiver', 'text', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
	sender = UserSerializer()
	receiver = serializers.SerializerMethodField()
	messages = MessageSerializer(many=True, read_only=True)
	messages_count = serializers.SerializerMethodField()

	class Meta:
		model = Conversation
		fields = ['id', 'channel_id', 'messages', 'messages_count', 'sender', 'receiver']

	def get_sender(self, obj):
		return obj.sender

	def get_receiver(self, obj):
		return obj.receiver

	def get_messages(self, obj):
		messages = Message.objects.filter(conversation=obj).order_by('timestamp')
		serializer = MessageSerializer(messages, many=True)
		return serializer.data

	def get_messages_count(self, obj):
		return obj.messages.count()
