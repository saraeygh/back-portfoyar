from django.urls import path

from samaneh.settings import DEBUG

from .test_view import TestView

test_urls = []
if DEBUG:
    test_urls = [
        path("test", TestView.as_view()),
    ]

urlpatterns = test_urls
