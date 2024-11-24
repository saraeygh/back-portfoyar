from django.urls import path

from samaneh.settings.common import DEBUG
from dashboard.routes import dashboard_ws_routes


test_urls = []
if DEBUG:
    from .test_consumer import TestConsumer

    test_urls = [
        path("ws/test/", TestConsumer.as_asgi()),
    ]

ws_urlpatterns = dashboard_ws_routes + test_urls
