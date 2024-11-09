from django.urls import path

from samaneh.settings.common import DEBUG

if DEBUG:
    from .test_consumer import TestConsumer

    test_urls = [
        path("ws/test/", TestConsumer.as_asgi()),
    ]

else:
    test_urls = []

from .test_consumer import TestConsumer

test_urls = [
    path("ws/test/", TestConsumer.as_asgi()),
]

ws_urlpatterns = [] + test_urls
