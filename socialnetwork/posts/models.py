import uuid
from django.db import models
from users.models import User

class Post(models.Model):
	id = models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False
	)

	body = models.TextField()

	author = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='author'
	)

	picture = models.ImageField(
		blank=True,
		null=True
	)

	created_at = models.DateTimeField(
		auto_now_add=True
	)

	def __str__(self):
		return str(self.author)

class Like(models.Model):
	id = models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False
	)

	post = models.ForeignKey(
		Post,
		related_name='likes',
		on_delete=models.CASCADE
	)

	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE
	)

	created_at = models.DateTimeField(
		auto_now_add=True
	)

	def __str__(self):
		return f"Like por {self.user.username}"

class Comment(models.Model):
	id = models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False
	)

	post = models.ForeignKey(
		Post,
		related_name='comments',
		on_delete=models.CASCADE
	)

	author = models.ForeignKey(
		User,
		on_delete=models.CASCADE
	)

	text = models.TextField()
	
	created_at = models.DateTimeField(
		auto_now_add=True
	)

	def __str__(self):
		return f"Comentário por {self.author.username}"
