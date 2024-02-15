import uuid
from django.db import models
from users.models import User

class Post(models.Model):
	id = models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False
	)

	title = models.CharField(
		max_length=50,
		blank=True
	)

	body = models.TextField()
	
	likes = models.ManyToManyField(
		User,
		blank=True
	)

	author = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='author'
	)

	picture = models.ImageField(
		blank=True,
		null=True
	)

	def __str__(self):
		return str(self.title)