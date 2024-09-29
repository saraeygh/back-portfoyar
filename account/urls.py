from django.urls import path
from core.views import CustomeObtainAuthToken

from account.views import (
    SignUpAPIView,
    UploadUsersAPIView,
    ProfileAPIView,
    EmailAPIView,
)


upload_users_urls = [
    path("upload-users/", UploadUsersAPIView.as_view()),
]

sign_in_sign_up_urls = [
    path("sign-up/", SignUpAPIView.as_view()),
    path("sign-in/", CustomeObtainAuthToken.as_view()),
]

edit_profile_urls = [
    path("profile/", ProfileAPIView.as_view()),
]

add_update_email_urls = [
    path("email/", EmailAPIView.as_view()),
]

urlpatterns = (
    upload_users_urls + sign_in_sign_up_urls + edit_profile_urls + add_update_email_urls
)
