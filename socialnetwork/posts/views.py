from rest_framework import viewsets, status
from rest_framework.response import Response
from users.models import User
from django.shortcuts import render, redirect
from .models import Post, Comment, Like
from django.http import JsonResponse
from .serializers import PostModelSerializer, PostCreateSerializer, PostUpdateSerializer, CommentModelSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.db.models import Q


def posts_page(request):
	return render(request, 'posts.html')

def postPage2(request, *args, **kwargs):
	user_posts = Post.objects.select_related('author').filter(
		Q(author=request.user) | Q(author__friends=request.user)
	).distinct()

	serialized_posts = PostModelSerializer(user_posts, many=True).data

	context = {
		'user_posts': serialized_posts
	}
	return render(request, "posts/postPage.html", context)


class PostViewsets(viewsets.ModelViewSet):
	queryset = Post.objects.all()
	serializer_class = PostModelSerializer

	JWT_authenticator = JWTAuthentication()

	def index(self, request):
		posts = Post.objects.all().order_by('-created_at')
		serializer = PostModelSerializer(posts, many=True, context={'request': request})
		return Response(serializer.data)

	def create(self, request, *args, **kwargs):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			serializer = PostCreateSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)

			picture = request.data.get('picture')
			if picture:
				image = Image.open(picture)
				image.thumbnail((240, 240), Image.BILINEAR)
				# Converter de volta para um arquivo mantendo o formato original
				output = BytesIO()
				image.save(output, format=image.format)
				output.seek(0)

				picture = InMemoryUploadedFile(
					output,
					'ImageField',
					"%s.%s" % (picture.name.split('.')[0], image.format.lower()),
					'image/%s' % image.format.lower(),
					sys.getsizeof(output),
					None
				)

			serializer.save(author=user, picture=picture)

			return JsonResponse({
				"message": 'Postagem criada com sucesso!',
			})
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)

	def retrieve(self, request, pk=None):
		post = Post.objects.filter(pk=pk).first()
		
		if post is None:
			return JsonResponse({"error": "A postagem informada não existe"}, status=404)

		serializer = PostModelSerializer(post)
		return JsonResponse(serializer.data)

	def update(self, request, *args, **kwargs):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			instance = self.get_object()

			if instance.author == user:
				partial = kwargs.pop('partial', False)
				serializer = PostUpdateSerializer(instance, data=request.data, partial=partial)
				serializer.is_valid(raise_exception=True)
				serializer.save()
				return JsonResponse({
					"message": 'Postagem atualizada com sucesso!',
				})
			else:
				return JsonResponse({
					"error": 'Você não tem permissão para atualizar esta postagem!',
				}, status=403)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)

	def destroy(self, request, *args, **kwargs):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			instance = self.get_object()

			if instance.author == user:
				self.perform_destroy(instance)
				return JsonResponse({
					"message": 'Postagem removida com sucesso!',
				})
			else:
				return JsonResponse({
					"error": 'Você não tem permissão para remover esta postagem',
				}, status=403)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)
		
	def like_post(self, request, pk):
		post = self.get_object()
		user = request.user
		
		if user.is_authenticated:
			if post.likes.filter(user=user).exists():
				return Response({"error": "Você já deu like nesse post."}, status=status.HTTP_400_BAD_REQUEST)
			else:
				Like.objects.create(post=post, user=user)
				return Response({"message": "Você deu um like."}, status=status.HTTP_201_CREATED)
		else:
			return Response({"error": "Usuário não autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

	def unlike_post(self, request, pk):
		post = self.get_object()
		user = request.user
		
		if user.is_authenticated:
			like = post.likes.filter(user=user).first()
			if like:
				like.delete()
				return Response({"message": "Like removido com sucesso."}, status=status.HTTP_200_OK)
			else:
				return Response({"error": "Você ainda não deu like nesse post."}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"error": "Usuário não autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

	def friends_posts(self, request):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			friends_ids = user.friends.values_list('id', flat=True)

			user_and_friends_posts = Post.objects.filter(
				Q(author=user) | Q(author__in=friends_ids)
			).distinct().order_by('-created_at')

			serializer = PostModelSerializer(user_and_friends_posts, many=True)

			return Response(serializer.data)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)

	@classmethod
	def as_view(cls, actions=None, **kwargs):
		actions['index'] = 'index'
		return super().as_view(actions=actions, **kwargs)

class CommentViewSet(viewsets.ModelViewSet):
	serializer_class = CommentModelSerializer

	JWT_authenticator = JWTAuthentication()

	def get_queryset(self):
		post_id = self.kwargs.get('post_id')
		if post_id is not None:
			return Comment.objects.filter(post_id=post_id)
		return Comment.objects.none()

	def create(self, request, post_id):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			post = get_object_or_404(Post, pk=post_id)
			if user == post.author or user in post.author.friends.all():
				serializer = CommentModelSerializer(data=request.data)
				if serializer.is_valid():
					serializer.save(post=post, author=request.user)
					return JsonResponse({
						"message": 'Comentário adicionado com sucesso!',
					}, status=status.HTTP_200_OK)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			else:
				return JsonResponse({
					"error": 'Você não tem permissão para adicionar comentários nsta postagem',
				}, status=401)

		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)

	def update(self, request, post_id, pk):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			comment = get_object_or_404(Comment, pk=pk, post_id=post_id)

			if user == comment.author:
				self.check_object_permissions(request, comment)
				serializer = CommentModelSerializer(comment, data=request.data)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({
						"message": 'Comentário atualizado com sucesso!',
					}, status=status.HTTP_200_OK)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			else:
				return JsonResponse({
					"error": 'Você não tem permissões para atualizar esse comentáro',
				}, status=403)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)	

	def destroy(self, request, post_id, pk):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			comment = get_object_or_404(Comment, pk=pk, post_id=post_id)
			if user == comment.author:
				comment.delete()
				return JsonResponse({
					"message": 'Comentário removido com sucesso!',
				}, status=status.HTTP_200_OK)
			else:
				return JsonResponse({
					"error": 'Este comentário somente o autor poderá remover',
				}, status=403)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)

