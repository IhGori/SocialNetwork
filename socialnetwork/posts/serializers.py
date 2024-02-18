from rest_framework import serializers
from users.models import User
from .models import Post, Like, Comment

class UserModelSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username')

class CommentModelSerializer(serializers.ModelSerializer):
	author = UserModelSerializer(read_only=True)
	class Meta:
		model = Comment
		fields = ('id', 'text', 'author', 'created_at')

class LikeModelSerializer(serializers.ModelSerializer):
	user = UserModelSerializer(read_only=True)

	class Meta:
		model = Like
		fields = ('user', 'created_at')

class PostModelSerializer(serializers.ModelSerializer):
	likes = LikeModelSerializer(many=True, read_only=True)
	author = serializers.SerializerMethodField()
	like_count = serializers.SerializerMethodField()
	comments = CommentModelSerializer(many=True, read_only=True)
	comments_count = serializers.SerializerMethodField()

	class Meta:
			model = Post
			fields = ('id', 'body', 'likes', 'author', 'like_count', 'picture', 'comments', 'created_at', 'comments_count')

	def get_author(self, obj):
		return obj.author.username
	
	def get_like_count(self, obj):
		return len(obj.likes.all())

	def get_comments_count(self, obj):
		return obj.comments.count()

class PostCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post
		fields = ('picture', 'body')

class PostUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post
		fields = ('picture', 'body')
