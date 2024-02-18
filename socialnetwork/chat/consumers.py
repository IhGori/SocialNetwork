import json

from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		logger.info("WebSocket connection established.")
		self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
		self.room_group_name = f"chat_{self.room_name}"

		# Join room group
		await self.channel_layer.group_add(self.room_group_name, self.channel_name)

		await self.accept()

	async def disconnect(self, close_code):
		logger.info("WebSocket connection closed.")
		await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

	async def receive(self, text_data):
		logger.info(f"Received message: {text_data}")
		text_data_json = json.loads(text_data)
		username = text_data_json["username"]
		message = text_data_json["message"]

		# Send message to room group
		await self.channel_layer.group_send(
			self.room_group_name, {"type": "chat.message", "username": username, "message": message}
		)

	# Receive message from room group
	async def chat_message(self, event):
		username = event["username"]
		message = event["message"]

		# Send message to WebSocket
		await self.send(text_data=json.dumps({"username": username, "message": message}))
