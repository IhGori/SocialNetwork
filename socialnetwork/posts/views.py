from rest_framework import viewsets, status
from rest_framework.response import Response
from users.models import User
from django.shortcuts import render, redirect
from .models import Post, Comment, Like
from django.http import JsonResponse
from .serializers import PostModelSerializer, PostCreateSerializer, PostUpdateSerializer, CommentModelSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import status

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

			text = request.data.get('body')
			picture = request.data.get('picture')

			serializer.save(author=user, picture=picture)
			
			channel_layer = get_channel_layer()
			async_to_sync(channel_layer.group_send)(
				'post_updates',
				{
					'type': 'post_created',
					'message': 'Nova postagem criada',
					'text': text
				}
			)
			return JsonResponse({
				"message": 'Postagem criada com sucesso!',
			}, status=status.HTTP_201_CREATED)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=status.HTTP_401_UNAUTHORIZED)

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
				updated_data = serializer.validated_data
				serializer.save()

				channel_layer = get_channel_layer()
				async_to_sync(channel_layer.group_send)(
					'post_updates',
					{
						'type': 'post_updated',
						'message': 'Postagem atualizada',
						'updated_data': updated_data
					}
				)
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
				channel_layer = get_channel_layer()
				async_to_sync(channel_layer.group_send)(
					'post_updates',
					{
						'type': 'post_deleted',
						'message': 'Post deletado'
					}
				)
				return JsonResponse({
					"message": 'Postagem removida com sucesso!',
				}, status=status.HTTP_204_NO_CONTENT)
			else:
				return JsonResponse({
					"error": 'Você não tem permissão para remover esta postagem',
				}, status=403)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)
		
	def like_post(self, request, *args, **kwargs):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			post = self.get_object()
			if post.likes.filter(user=user).exists():
					return Response({"error": "Você já deu like nesse post."}, status=status.HTTP_400_BAD_REQUEST)
			else:
				Like.objects.create(post=post, user=user)
				channel_layer = get_channel_layer()
				async_to_sync(channel_layer.group_send)(
					'post_updates',
					{
						'type': 'like_created',
						'message': 'Like adicionado'
					}
				)
				return Response({"message": "Você deu um like."}, status=status.HTTP_201_CREATED)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)

	def unlike_post(self, request, pk):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			post = self.get_object()
			like = post.likes.filter(user=user).first()
			if like:
				like.delete()
				channel_layer = get_channel_layer()
				async_to_sync(channel_layer.group_send)(
					'post_updates',
					{
						'type': 'like_deleted',
						'message': 'Like adicionado'
					}
				)
				return Response({"message": "Like removido com sucesso."}, status=status.HTTP_200_OK)
			else:
				return Response({"error": "Você ainda não deu like nesse post."}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return JsonResponse({
				"error": 'Token de acesso ausente ou inválido',
			}, status=401)

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

					updated_data = serializer.validated_data

					channel_layer = get_channel_layer()
					async_to_sync(channel_layer.group_send)(
						'post_updates',
						{
							'type': 'comment_created',
							'message': 'Comentário adicionado',
							'created_comment': updated_data
						}
					)
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
					channel_layer = get_channel_layer()
					async_to_sync(channel_layer.group_send)(
						'post_updates',
						{
							'type': 'comment_updated',
							'message': 'Comentário atualizado'
						}
					)
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
				channel_layer = get_channel_layer()
				async_to_sync(channel_layer.group_send)(
					'post_updates',
					{
						'type': 'comment_deleted',
						'message': 'Comentário deletado'
					}
				)
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

