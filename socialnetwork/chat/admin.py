from django.contrib import admin
from .models import Message, Conversation

class MessageAdmin(admin.ModelAdmin):
	list_display = ('sender', 'receiver', 'text', 'timestamp')
	readonly_fields = ('timestamp',)
	list_filter = ('sender', 'receiver', 'timestamp')

admin.site.register(Message, MessageAdmin)

admin.site.register(Conversation)