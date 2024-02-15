from rest_framework import serializers
from users.models import User
from .models import Post

class UserModelSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username')

class PostModelSerializer(serializers.ModelSerializer):
	likes = UserModelSerializer(many=True, read_only=True)
	author = serializers.SerializerMethodField()
	like_count = serializers.SerializerMethodField()
	is_liked = serializers.SerializerMethodField()

	class Meta:
			model = Post
			fields = ('id', 'title', 'body', 'likes', 'author', 'like_count', 'is_liked', 'picture')
	
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