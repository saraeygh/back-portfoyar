import re
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response

from core.configs import PHONE_PATTERN


def is_valid_phone(phone):
    match = re.match(PHONE_PATTERN, phone)
    if match:
        return True
    else:
        return False


def is_valid_username(username):
    user_exists = User.objects.filter(username=username).exists()
    if username is not None and is_valid_phone(username) and not user_exists:
        return True, ""
    return False, Response(
        {"message": "شماره موبایل نامعتبر، اگر حساب کاربری دارید، وارد شوید"},
        status=status.HTTP_400_BAD_REQUEST,
    )
