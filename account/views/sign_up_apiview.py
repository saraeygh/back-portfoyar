import os
import re
import random
import string
import json
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle

from melipayamak.melipayamak import Api

from core.utils import RedisInterface
from core.configs import KEY_WITH_EX_REDIS_DB

from account.serializers import SignUpSerializer
from colorama import Fore, Style


class SignUpAPIView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# V2-SIGNUP

REDIS_PREFIX_CODE_TEXT = "username_verify_code_"
OLD_PASSWORD = "old_password"
NEW_PASSWORD = "new_password"

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
    code_key = REDIS_PREFIX_CODE_TEXT + f"{username}"
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
    code_key = REDIS_PREFIX_CODE_TEXT + f"{username}"
    code_info = redis_conn.client.get(code_key)
    return None if code_info is None else json.loads(code_info.decode("utf-8"))


def generate_password():
    ASCII_LETTERS = string.ascii_letters
    ASCII_LETTERS.replace("I", "")
    ASCII_LETTERS.replace("l", "")
    DIGITS = string.digits
    PUNC = "#$@&"

    PASS_LEN = 9
    password = ""
    password += random.choice(ASCII_LETTERS)

    CHAR_LIST = [ASCII_LETTERS, DIGITS, PUNC]
    for _ in range(PASS_LEN):
        character_type = random.choice(CHAR_LIST)
        password += random.choice(character_type)

    return password


def password_is_valid(password):
    try:
        validate_password(password)
        return True
    except Exception as e:
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)
        return False


def change_user_password(user, new_password):
    user.set_password(new_password)
    user.save()


class V2SignUpAPIView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        username = request.data.get("username")
        user_exists = User.objects.filter(username=username).exists()
        if username is None or not is_valid_phone(username) or user_exists:
            return Response(
                {"message": "شماره موبایل نامعتبر"}, status=status.HTTP_400_BAD_REQUEST
            )

        code = str(random.randint(123456, 999999))
        token = uuid4().hex
        code_saved_in_redis = set_dict_in_redis(
            {"username": username, "code": code, "token": token}
        )

        if not code_saved_in_redis:
            return Response(
                {"message": "بعد از گذشت ۵ دقیقه دوباره تلاش کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # response = send_sms_code(username, code)
        response = "Ok"
        if response == "Ok":
            return Response(
                {"message": "کد تایید ارسال شد", "token": token},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "متاسفانه کد ارسال نشد، بعد از چند دقیقه دوباره تلاش کنید"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request):
        username = str(request.data.get("username"))
        code_info = get_dict_from_redis(username)
        if code_info is None:
            return Response(
                {"message": "کد منقضی شده است، لطفا دوباره تلاش کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sent_token = str(request.data.get("token"))
        generated_token = code_info.get("token")
        if sent_token != generated_token:
            return Response(
                {"message": "درخواست نامعتبر"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sent_code = str(request.data.get("code"))
        generated_code = code_info.get("code")
        if sent_code != generated_code:
            return Response(
                {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
            )

        password = str(request.data.get("password"))
        if not password_is_valid(password):
            return Response(
                {
                    "message": "رمز عبور انتخابی امن نیست، لطفاً یک رمز عبور قوی‌تر انتخاب کنید"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_user = User(username=username)
        new_user.set_password(password)
        new_user.save()

        authenticated_user = authenticate(
            request=request, username=username, password=password
        )
        if authenticated_user is None:
            return Response(
                {"message": "مشکلی پیش آمده است، با پشتیبانی تماس بگیرید"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "حساب کاربری شما با موفقیت ایجاد شد"},
            status=status.HTTP_200_OK,
        )
