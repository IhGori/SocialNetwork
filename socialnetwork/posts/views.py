from rest_framework import viewsets, status
from rest_framework.response import Response
from users.models import User
from django.shortcuts import render, redirect
from .models import Post
from django.http import JsonResponse
from .serializers import PostModelSerializer, PostCreateSerializer, PostUpdateSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Q

def postPage(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return redirect("login-user")

	user_posts = Post.objects.filter(
		Q(author=request.user) | Q(author__friends=request.user)
	).distinct()
	
	context = {
		'user_posts': user_posts
	}
	return render(request, "posts/postPage.html", context)


class PostViewsets(viewsets.ModelViewSet):
	queryset = Post.objects.all()
	serializer_class = PostModelSerializer

	JWT_authenticator = JWTAuthentication()

	def index(self, request):
		posts = Post.objects.all()
		serializer = PostModelSerializer(posts, many=True, context={'request': request})
		return Response(serializer.data)

	def create(self, request, *args, **kwargs):
		response = self.JWT_authenticator.authenticate(request)
		
		if response is not None:
			user, token = response

			serializer = PostCreateSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			serializer.save(author=user)

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
		if request.user in post.likes.all():
			return Response({"error": "Você já deu like nesse post."}, status=status.HTTP_400_BAD_REQUEST)
		post.likes.add(request.user)

		return Response({"message": "Você deu um like."}, status=status.HTTP_201_CREATED)

	def unlike_post(self, request, pk):
		post = self.get_object()
		if request.user not in post.likes.all():
			return Response({"error": "Você ainda não deu like nesse post."}, status=status.HTTP_400_BAD_REQUEST)
		post.likes.remove(request.user)

		return Response({"message": "Like removido com sucesso."}, status=status.HTTP_204_NO_CONTENT)


	@classmethod
	def as_view(cls, actions=None, **kwargs):
		actions['index'] = 'index'
		return super().as_view(actions=actions, **kwargs)
