import json
import random

from django.core.validators import validate_email

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.configs import (
    KEY_WITH_EX_REDIS_DB,
    EMAIL_VERIFY_CODE_EXPIRY,
    REDIS_EMAIL_VERIFY_PREFIX,
)
from core.utils import RedisInterface

from account.utils import send_email_verify_code


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except Exception:
        return False


def set_dict_in_redis(code_info: dict):
    username = code_info.get("username")
    code_info = json.dumps(code_info)

    code_key = REDIS_EMAIL_VERIFY_PREFIX + f"{username}"
    expiration_time = EMAIL_VERIFY_CODE_EXPIRY
    redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)
    redis_conn.client.delete(code_key)
    redis_conn.client.set(code_key, code_info, ex=expiration_time)
    redis_conn.client.close()


def get_dict_from_redis(username):
    code_key = REDIS_EMAIL_VERIFY_PREFIX + f"{username}"
    redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)
    code_info = redis_conn.client.get(code_key)
    redis_conn.client.close()

    return None if code_info is None else json.loads(code_info.decode("utf-8"))


def create_email_verify_code(request):
    email = request.data.get("email")
    if email is None or not is_valid_email(email):
        return Response(
            {"message": "ایمیل نامعتبر"}, status=status.HTTP_400_BAD_REQUEST
        )

    username = request.user.username
    code = str(random.randint(123456, 999999))
    set_dict_in_redis({"username": username, "email": email, "code": code})
    sent = send_email_verify_code(username, email, code)
    if sent:
        return Response({"message": "کد تایید ارسال شد"}, status=status.HTTP_200_OK)
    return Response(
        {"message": "متاسفانه کد تایید ارسال نشد، دوباره تلاش کنید"},
        status=status.HTTP_400_BAD_REQUEST,
    )


def verify_email(request):
    sent_code = str(request.data.get("code"))
    user = request.user
    code_info = get_dict_from_redis(user.username)
    if code_info is None:
        return Response(
            {"message": "کد منقضی شده است، لطفا دوباره تلاش کنید"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    generated_code = code_info.get("code")
    if sent_code == generated_code:
        new_email = code_info.get("email")
        user.email = new_email
        user.save()
        return Response({"message": "ایمیل به‌روزرسانی شد"}, status=status.HTTP_200_OK)

    return Response(
        {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
    )


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class EmailAPIView(APIView):
    def get(self, request):
        email = {"email": request.user.email}
        return Response(email, status=status.HTTP_200_OK)

    def post(self, request):
        email = request.data.get("email")
        sent_code = request.data.get("code")

        if email:
            return create_email_verify_code(request)
        elif sent_code:
            return verify_email(request)
        else:
            return Response(
                {"message": "مشکلی پیش آمده است"}, status=status.HTTP_400_BAD_REQUEST
            )
