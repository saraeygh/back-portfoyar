from django.urls import path

from samaneh.settings import DEBUG

from .test_view import TestView
from .new_user_report_apiview import NewUserAPIView

test_urls = [
    path("new-user-report", NewUserAPIView.as_view()),
]

if DEBUG:
    test_urls = test_urls + [
        path("test", TestView.as_view()),
    ]

urlpatterns = test_urls
