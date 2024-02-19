import factory
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import User
from .serializers import *

class UserFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = User

	username = factory.Sequence(lambda n: f'user{n}')
	password = 'testpassword'
	email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
	phone = '1234567890'
	gender = 'M'

	@classmethod
	def data(cls):
		instance = cls.build()
		serializer = CreateUserSerializer(instance=instance)
		return serializer.data

class UserAPITest(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.register_url = reverse('users:register')
		self.login_url = reverse('users:login')
		self.user1_data = UserFactory.build()
		self.user2_data = UserFactory.build()

	def test_register_user(self):
		# Registra um usuário
		response = self.client.post(self.register_url, {
			'username': self.user1_data.username,
			'password': self.user1_data.password,
			'password2': self.user1_data.password,
			'email': self.user1_data.email,
			'gender': self.user1_data.gender,
			'phone': self.user1_data.phone,
		}, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		# Verifica se o usuário criado existe
		self.assertTrue(User.objects.filter(username=self.user1_data.username).exists())

	def test_login_user(self):
		# Registra um usuário
		self.client.post(self.register_url, {
			'username': self.user2_data.username,
			'password': self.user2_data.password,
			'password2': self.user2_data.password,
			'email': self.user2_data.email,
			'gender': self.user2_data.gender,
			'phone': self.user2_data.phone,
		}, format='json')

		# Faz login com as credenciais do usuário cadastrado
		response = self.client.post(self.login_url, {
			'username': self.user2_data.username,
			'password': self.user2_data.password
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		# Verifique se a resposta contém tokens e alguns campos do usuário
		tokens = response.json().get('tokens')
		self.assertIsNotNone(tokens)

		user = response.json().get('user')
		self.assertIsNotNone(user)
		self.assertEqual(user['username'], self.user2_data.username)
		self.assertEqual(user['email'], self.user2_data.email)

	def test_update_user(self):
		# Registra um usuário
		response = self.client.post(self.register_url, {
			'username': self.user1_data.username,
			'password': self.user1_data.password,
			'password2': self.user1_data.password,
			'email': self.user1_data.email,
			'gender': self.user1_data.gender,
			'phone': self.user1_data.phone,
		}, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		# Obtém o objeto usuário
		user = User.objects.get(username=self.user1_data.username)

		# Atualize os dados do usuário
		updated_data = {
			'username': 'updated_username',
			'email': 'updated@example.com'
		}
		update_url = reverse('users:user-detail', kwargs={'user_id': user.id})
		response = self.client.patch(update_url, updated_data, format='json')

		# Verifique se a atualização foi bem sucedida
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['username'], updated_data['username'])
		self.assertEqual(response.data['email'], updated_data['email'])

	def test_delete_user(self):
		# Cria e preserva o usuário
		user1 = UserFactory.create()

		delete_url = reverse('users:user-detail', kwargs={'user_id': user1.id})
		response = self.client.delete(delete_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(User.objects.filter(id=user1.id).exists())
