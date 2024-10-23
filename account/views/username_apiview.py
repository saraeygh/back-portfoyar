import os
import re
import json
import smtplib
import random

from django.contrib.auth.models import User

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from melipayamak.melipayamak import Api

from core.utils import RedisInterface
from core.configs import KEY_WITH_EX_REDIS_DB

redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)


def is_valid_phone(phone):
    PHONE_PATTERN = r"^09(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|7[0-9]|8[0-9]|9[0-9])-?[0-9]{3}-?[0-9]{4}$"
    match = re.match(PHONE_PATTERN, phone)
    if match:
        return True
    else:
        return False


def set_dict_in_redis(code_info: dict):
    username = code_info.get("username")
    code_key = f"username_verify_code_{username}"
    old_code_info = redis_conn.client.get(code_key)
    if old_code_info is not None:
        return False

    code_info = json.dumps(code_info)
    expiration_time = 60 * 5
    redis_conn.client.set(code_key, code_info, ex=expiration_time)
    return True


def send_sms_code(to, code):
    MELIPAYAMAK_USERNAME = os.environ.setdefault("MELIPAYAMAK_USERNAME", "09102188113")
    MELIPAYAMAK_PASSOWRD = os.environ.setdefault("MELIPAYAMAK_PASSOWRD", "TL5OC")
    api = Api(MELIPAYAMAK_USERNAME, MELIPAYAMAK_PASSOWRD)
    sms = api.sms()
    response = sms.send_by_base_number(text=code, to=to, bodyId=92005)
    response = response.get("StrRetStatus")
    return response


def get_dict_from_redis(username):
    code_key = f"username_verify_code_{username}"
    code_info = redis_conn.client.get(code_key)
    return None if code_info is None else json.loads(code_info.decode("utf-8"))


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class UsernameAPIView(APIView):
    def get(self, request):
        username = {"username": request.user.username}
        return Response(username, status=status.HTTP_200_OK)

    def post(self, request):
        new_username = request.data.get("username")
        user_exists = User.objects.filter(username=new_username).exists()
        if new_username is None or not is_valid_phone(new_username) or user_exists:
            return Response(
                {"message": "شماره موبایل نامعتبر"}, status=status.HTTP_400_BAD_REQUEST
            )

        username = request.user.username
        code = str(random.randint(123456, 999999))
        code_saved_in_redis = set_dict_in_redis(
            {"username": username, "new_username": new_username, "code": code}
        )
        if not code_saved_in_redis:
            return Response(
                {"message": "بعد از گذشت ۵ دقیقه دوباره تلاش کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = send_sms_code(new_username, code)
        if response == "Ok":
            return Response({"message": "کد تایید ارسال شد"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "متاسفانه کد ارسال نشد، بعد از ۵ دقیقه دوباره تلاش کنید"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request):
        sent_code = str(request.data.get("code"))
        user: User = request.user
        code_info = get_dict_from_redis(user.username)
        if code_info is None:
            return Response(
                {"message": "کد منقضی شده است، لطفا دوباره تلاش کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        generated_code = code_info.get("code")
        if sent_code == generated_code:
            new_username = code_info.get("new_username")
            user.username = new_username
            user.save()
            return Response(
                {"message": "نام کاربری به‌روزرسانی شد"}, status=status.HTTP_200_OK
            )

        return Response(
            {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
        )
