from django.urls import path

from samaneh.settings.common import DEBUG
from stock_market.routes import marketwatch_ws_routes


test_urls = []
if DEBUG:
    from .test_consumer import TestConsumer

    test_urls = [
        path("ws/test/", TestConsumer.as_asgi()),
    ]

ws_urlpatterns = marketwatch_ws_routes + test_urls
