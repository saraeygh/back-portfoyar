import json

from django.urls import path
from channels.routing import URLRouter

from channels.generic.websocket import WebsocketConsumer


class TestConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        self.send(text_data=json.dumps({"message": message}))


test_ws_routes = [
    path("", TestConsumer.as_asgi()),
]


test_router = URLRouter(test_ws_routes)
