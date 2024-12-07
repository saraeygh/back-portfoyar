from django.urls import path
from core.views import CustomObtainAuthToken

from account.views import (
    PricingAPIView,
    SignUpAPIView,
    UploadUsersAPIView,
    ProfileAPIView,
    EmailAPIView,
    UsernameAPIView,
    PasswordAPIView,
    ResetPasswordAPIView,
)


upload_users_urls = [
    path("upload-users/", UploadUsersAPIView.as_view()),
]

sign_in_sign_up_urls = [
    path("sign-up/", SignUpAPIView.as_view()),
    path("sign-in/", CustomObtainAuthToken.as_view()),
]

profile_urls = [
    path("profile/", ProfileAPIView.as_view()),
]

email_urls = [
    path("email/", EmailAPIView.as_view()),
]

credential_urls = [
    path("reset-password/", ResetPasswordAPIView.as_view()),
    path("password/", PasswordAPIView.as_view()),
    path("username/", UsernameAPIView.as_view()),
]

subscription_urls = [
    path("pricing/", PricingAPIView.as_view()),
]

urlpatterns = (
    upload_users_urls
    + sign_in_sign_up_urls
    + profile_urls
    + email_urls
    + credential_urls
    + subscription_urls
)
