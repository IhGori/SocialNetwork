from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import User

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

	profile_picture = serializers.ImageField(
		required=False
	)

	class Meta:
		fields = ('username', 'email', 'password', 'phone', 'gender')

class UserSerializer(BaseUserSerializer):
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