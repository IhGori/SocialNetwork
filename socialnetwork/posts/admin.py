from django.contrib import admin
from .models import Post, Comment, Like

class PostAdmin(admin.ModelAdmin):
	list_display = ('author', 'created_at', 'total_likes', 'total_comments')
	list_filter = ('author', 'created_at')
	search_fields = ('body', 'author__username')
	readonly_fields = ('id', 'created_at')

	def get_criado_em(self, obj):
		return obj.created_at.strftime('%d/%m/%Y %H:%M')

	def total_likes(self, obj):
		return obj.likes.count()

	def total_comments(self, obj):
		return obj.comments.count()

admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
	list_display= ('author', 'created_at')
	list_filter = ('author', 'created_at')
	search_fields = ('author', 'created_at')

admin.site.register(Comment, CommentAdmin)

class LikeAdmin(admin.ModelAdmin):
	list_display= ('post', 'user', 'created_at')
	list_filter = ('user', 'created_at')
	search_fields = ('user', 'created_at')

admin.site.register(Like, LikeAdmin)