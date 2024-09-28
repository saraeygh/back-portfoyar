from django.urls import path

from account.views import SignUpAPIView, UploadUsersAPIView


urlpatterns = [
    path("sign-up/", SignUpAPIView.as_view()),
    path("upload-users/", UploadUsersAPIView.as_view()),
]
