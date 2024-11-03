from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken import views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from core.utils import persian_numbers_to_english
from account.models import Profile

ACCOUNT_BANNED = "ACCOUNT_BANNED"


def get_user(request):
    username = persian_numbers_to_english(request.data.get("username"))
    user = User.objects.filter(username=username)
    if user.exists():
        return user.first(), ""
    return False, Response(
        data={"message": "اطلاعات اشتباه است"}, status=status.HTTP_406_NOT_ACCEPTABLE
    )


def check_max_logins(user):
    profile: Profile = user.profile
    max_logins = profile.max_login
    active_logins = profile.active_login

    if max_logins < 1:
        Token.objects.filter(user=user).delete()
        return ACCOUNT_BANNED
    elif active_logins + 1 > max_logins:
        Token.objects.filter(user=user).delete()
        profile.active_login = 1
    else:
        profile.active_login = active_logins + 1

    profile.save()


def get_full_name(user: User):
    full_name = user.get_full_name()
    if full_name is None or full_name == "":
        full_name = user.username
    return full_name


class CustomObtainAuthToken(views.ObtainAuthToken):
    def post(self, request, *args, **kwargs) -> Response:
        user, response = get_user(request)
        if not user:
            return response
        result = check_max_logins(user)
        if result == ACCOUNT_BANNED:
            return Response(
                data={"message": "حساب شما مسدود شده است"},
                status=status.HTTP_403_FORBIDDEN,
            )
        response = super().post(request, *args, **kwargs)
        token = response.data.get("token")
        full_name = get_full_name(user)

        return Response(
            data={"token": token, "full_name": full_name}, status=status.HTTP_200_OK
        )
