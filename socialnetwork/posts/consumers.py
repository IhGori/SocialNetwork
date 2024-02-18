import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Post, Comment, Like

class PostUpdateConsumer(WebsocketConsumer):
	def connect(self):
		self.room_group_name = 'post_updates'

		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name
		)

		self.accept()

	def disconnect(self, close_code):
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name,
			self.channel_name
		)

	def send_post_update(self, event):
		self.send(text_data=json.dumps(event))

	def receive(self, text_data):
		pass

	def post_created(self, event):
		self.send_post_update(event)

	def comment_created(self, event):
		self.send_post_update(event)

	def like_created(self, event):
		self.send_post_update(event)

	def post_updated(self, event):
		self.send_post_update(event)

	def post_deleted(self, event):
		self.send_post_update(event)

	def comment_updated(self, event):
		self.send_post_update(event)

	def comment_deleted(self, event):
		self.send_post_update(event)

	def like_deleted(self, event):
		self.send_post_update(event)