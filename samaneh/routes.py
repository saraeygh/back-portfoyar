from django.urls import path

from samaneh.settings.common import DEBUG

# from stock_market.routes import marketwatch_ws_routes

ws_test_urls = []
if DEBUG:
    from .test_consumer import TestConsumer

    ws_test_urls = [
        path("ws/test", TestConsumer.as_asgi()),
    ]

ws_urlpatterns = ws_test_urls  # + marketwatch_ws_routes
