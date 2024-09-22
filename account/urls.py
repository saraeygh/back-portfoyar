from django.urls import path

from account.views import SignUpAPIView


urlpatterns = [
    path("sign-up/", SignUpAPIView.as_view()),
]
