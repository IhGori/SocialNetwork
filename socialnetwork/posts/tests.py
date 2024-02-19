from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from users.models import User
from users.serializers import CreateUserSerializer
from rest_framework.test import APIClient
from posts.models import Post
import factory
from django.utils import timezone

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
	
class BaseAPITest(APITestCase):
	def setUp(self):
		self.client = APIClient()
		self.register_url = reverse('users:register')
		self.login_url = reverse('users:login')
		self.user1_data = UserFactory.build()
		self.post = None

	def create_user_and_login(self, username, password):
		self.client.post(self.register_url, {
			'username': self.user1_data.username,
			'password': self.user1_data.password,
			'password2': self.user1_data.password,
			'email': self.user1_data.email,
			'gender': self.user1_data.gender,
			'phone': self.user1_data.phone,
		}, format='json')

		response = self.client.post(self.login_url, {
			'username': self.user1_data.username,
			'password': self.user1_data.password
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		tokens = response.json().get('tokens')
		self.assertIsNotNone(tokens)
		return tokens['access']

class PostAPITest(BaseAPITest):
	def setUp(self):
		super().setUp()
		self.access_token = self.create_user_and_login(username='testuser', password='testpassword')
		self.create_url = reverse('posts:posts-list')
		self.post = None  # para armazenar o objeto de postagem

	def create_post(self):
		# Cria uma postagem usando o token de acesso
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		data = {'body': 'Test Post Body'}
		response = self.client.post(self.create_url, data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

		# Armazena o objeto de postagem criado para uso posterior
		self.post = Post.objects.latest('id')

	def test_create_post(self):
		# Garante que o usuário está autenticado antes de criar a postagem
		self.assertIsNotNone(self.access_token)

		# Chama o método de criação de postagem
		self.create_post()

		# Verifica se a postagem foi criada corretamente
		self.assertIsNotNone(self.post)

	def test_update_post(self):
		# Garante que uma postagem tenha sido criada antes de tentar atualizá-la
		if self.post is None:
			self.create_post()

		# Atualiza a postagem usando o token de acesso
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		update_url = reverse('posts:posts-detail', kwargs={'pk': self.post.pk})
		updated_data = {'body': 'Updated Test Post Body'}
		response = self.client.put(update_url, updated_data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		# Verifica se a postagem foi realmente atualizada no banco de dados
		self.post.refresh_from_db()
		self.assertEqual(self.post.body, 'Updated Test Post Body')

	def test_delete_post(self):
		if self.post is None:
			self.create_post()

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		delete_url = reverse('posts:posts-detail', kwargs={'pk': self.post.pk})
		response = self.client.delete(delete_url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

		with self.assertRaises(Post.DoesNotExist):
			self.post.refresh_from_db()