import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
	id = models.UUIDField(
		primary_key=True,
		default=uuid.uuid4,
		editable=False
	)

	phone = models.CharField(
		'Telefone',
		max_length=20,
		blank=True,
		null=True
	)

	GENDER_CHOICES = [
		('F', 'Feminino'),
		('M', 'Masculino'),
		('N', 'Neutro'),
	]

	gender = models.CharField(
		'Gênero', max_length=1,
		choices=GENDER_CHOICES,
		blank=True,
		null=True
	)

	is_verified = models.BooleanField(
		'Verificado',
		default=False
	)

	friends = models.ManyToManyField(
		'self',
		verbose_name='Amigos',
		blank=True
	)

	picture = models.ImageField(
		blank=True,
		null=True,
	)