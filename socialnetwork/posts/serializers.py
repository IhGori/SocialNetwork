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
	is_liked = serializers.SerializerMethodField()
	comments = CommentModelSerializer(many=True, read_only=True)

	class Meta:
			model = Post
			fields = ('id', 'title', 'body', 'likes', 'author', 'like_count', 'is_liked', 'picture', 'comments')
	
	def get_author(self, obj):
		return obj.author.username
	
	def get_like_count(self, obj):
		return len(obj.likes.all())
	
	def get_is_liked(self, obj):
		request = self.context.get('request', None)
		if request and request.user.is_authenticated:
			return obj.likes.filter(id=request.user.id).exists()
		return False
	
class PostCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post
		fields = ('title', 'picture', 'body')

class PostUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post
		fields = ('title', 'picture', 'body')
