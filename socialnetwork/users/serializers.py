from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import User
import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

class BaseUserSerializer(serializers.ModelSerializer):
	gender_choices = (
		('M', 'Masculino'),
		('F', 'Feminino'),
		('N', 'Não especificado'),
	)

	username = serializers.CharField(
		validators=[UnicodeUsernameValidator()],
		max_length=150,
		min_length=3,
		error_messages={
			'max_length': 'O campo usuário não pode ser maior que 150 caracteres.',
			'min_length': 'O campo usuário não pode ser menor que 3 caracteres.',
		},
		required=False,
	)

	email = serializers.EmailField(
		validators=[UniqueValidator(queryset=User.objects.all())],
		error_messages={
			'invalid': 'Por favor, informe um e-mail válido.',
			'unique': 'O e-mail informado já está em uso.'
		},
		required=False
	)

	password = serializers.CharField(
		write_only=True,
		required=False
	)

	phone = serializers.CharField(
		max_length=13,
		min_length=10,
		required=False
	)

	gender = serializers.ChoiceField(
		choices=gender_choices,
		required=False
	)

	picture = serializers.ImageField(
		required=False
	)
	
	friends = serializers.SerializerMethodField()

	class Meta:
		fields = ('username', 'email', 'password', 'phone', 'gender', 'friends', 'picture')

	def get_friends(self, obj):
		friends = obj.friends.all()
		return [{'id': friend.id, 'username': friend.username} for friend in friends]

class UserSerializer(BaseUserSerializer):
	password2 = serializers.CharField(
		write_only=True,
		required=True,
		error_messages={
			'required': 'Por favor, confirme a sua senha.',
		}
	)

	id = serializers.UUIDField()
	class Meta:
		model = User
		fields = BaseUserSerializer.Meta.fields + ('id', 'password2')

	def validate(self, attrs):
		if attrs['password'] != attrs['password2']:
			raise serializers.ValidationError("A senha e confirmação de senha não são iguais.")
		return attrs

	def create(self, validated_data):
		password = validated_data.pop('password2', None)
		instance = self.Meta.model(**validated_data)
		if password is not  None:
			instance.set_password(password)
		instance.save()
		return instance

class UserUpdateSerializer(BaseUserSerializer):
	class Meta:
		model = User
		fields = BaseUserSerializer.Meta.fields

	def update(self, instance, validated_data):
		password = validated_data.pop('password', None)
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		if password is not None:
			instance.set_password(password)
		instance.save()
		return instance

class CreateUserSerializer(BaseUserSerializer):
	password2 = serializers.CharField(
		write_only=True,
		required=True,
		error_messages={
			'required': 'Por favor, confirme a sua senha.',
		}
	)

	class Meta:
		model = User
		fields = BaseUserSerializer.Meta.fields + ('password2',)

	def validate(self, attrs):
		if attrs['password'] != attrs['password2']:
			raise serializers.ValidationError("A senha e confirmação de senha não são iguais.")
		return attrs

	def create(self, validated_data):
		password = validated_data.pop('password2', None)
		picture = validated_data.pop('picture', None)

		instance = self.Meta.model(**validated_data)
		if picture is not None:
			img = Image.open(picture)
			img = img.convert('RGB')
			width, height = img.size

			left = (width - 240) / 2
			top = (height - 240) / 2
			right = (width + 240) / 2
			bottom = (height + 240) / 2

			img_cropped = img.crop((left, top, right, bottom))

			img_resized = img_cropped.resize((240, 240))

			output_buffer = BytesIO()

			img_resized.save(output_buffer, format='JPEG')

			output_buffer.seek(0)
			picture_temp = InMemoryUploadedFile(output_buffer, None, os.path.basename(picture.name), 'image/jpeg', output_buffer.getbuffer().nbytes, None)

			instance.picture = picture_temp

		if password is not None:
			instance.set_password(password)

		instance.save()
		return instance
