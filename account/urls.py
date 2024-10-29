from django.urls import path
from core.views import CustomeObtainAuthToken

from account.views import (
    SignUpAPIView,
    V2SignUpAPIView,
    UploadUsersAPIView,
    ProfileAPIView,
    EmailAPIView,
    UsernameAPIView,
    PasswordAPIView,
)


upload_users_urls = [
    path("upload-users/", UploadUsersAPIView.as_view()),
]

sign_in_sign_up_urls = [
    path("sign-up/", SignUpAPIView.as_view()),
    path("v2/sign-up/", V2SignUpAPIView.as_view()),
    path("sign-in/", CustomeObtainAuthToken.as_view()),
]

profile_urls = [
    path("profile/", ProfileAPIView.as_view()),
]

email_urls = [
    path("email/", EmailAPIView.as_view()),
]

credential_urls = [
    path("username/", UsernameAPIView.as_view()),
    path("password/", PasswordAPIView.as_view()),
]

urlpatterns = (
    upload_users_urls
    + sign_in_sign_up_urls
    + profile_urls
    + email_urls
    + credential_urls
)
