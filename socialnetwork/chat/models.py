from django.db import models
from users.models import User
import uuid

class Conversation(models.Model):
	channel_id = models.CharField(
		max_length=255,
		unique=True
	)

	def __str__(self):
		return str(self.channel_id)


class Message(models.Model):
	id = models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False
	)

	conversation = models.ForeignKey(
		Conversation,
		related_name='messages',
		on_delete=models.CASCADE
	)

	sender = models.ForeignKey(
		User,
		related_name='sent_messages',
		on_delete=models.CASCADE
	)

	receiver = models.ForeignKey(
		User,
		related_name='received_messages',
		on_delete=models.CASCADE,
		blank=False
	)

	text = models.TextField(
		blank=False
	)

	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.conversation)