import os
import re
import random
import json
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from samaneh.settings.common import DEBUG

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from melipayamak.melipayamak import Api


from core.utils import (
    RedisInterface,
    SEND_SIGNUP_SMS_STATUS,
    DAILY_SIGNUP_TRY_LIMITATION,
    persian_numbers_to_english,
)
from core.configs import (
    KEY_WITH_EX_REDIS_DB,
    PHONE_PATTERN,
    REDIS_PREFIX_CODE_TEXT,
    MELIPAYAMAK_OK_RESPONSE,
    SIGNUP_CODE_EXPIRY,
    SIGNUP_CODE_RANGE_MIN,
    SIGNUP_CODE_RANGE_MAX,
    SIGNUP_TRY_COUNT_EXPIRY,
    SIGNUP_DAILY_TRY_COUNT,
)
from core.models import ACTIVE, FeatureToggle

from colorama import Fore, Style


redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)


def check_daily_signup_limitation(request):
    check_try_limitation = FeatureToggle.objects.filter(
        name=DAILY_SIGNUP_TRY_LIMITATION
    ).first()

    if check_try_limitation.state == ACTIVE:
        ip = request.META.get("REMOTE_ADDR", "")
        tried_count = redis_conn.client.get(ip)
        if tried_count is None:
            redis_conn.client.set(ip, 1, ex=SIGNUP_TRY_COUNT_EXPIRY)
            return False, ""

        else:
            today_tried_count = int((redis_conn.client.get(ip)).decode("utf-8"))
            today_tried_count += 1
            if today_tried_count > SIGNUP_DAILY_TRY_COUNT and not DEBUG:
                limit_hours = int(SIGNUP_TRY_COUNT_EXPIRY / 3600)
                return True, Response(
                    {
                        "message": f"تعداد تلاش‌های شما بیشتر از حد مجاز ({SIGNUP_DAILY_TRY_COUNT}) شده است، لطفاً بعد از گذشت {limit_hours} ساعت دوباره تلاش کنید"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                time_left = redis_conn.client.ttl(ip)
                redis_conn.client.set(ip, today_tried_count, ex=time_left)

                return False, ""

    else:
        return False, ""


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


def set_dict_in_redis(code_info: dict):
    username = code_info.get("username")
    code_key = REDIS_PREFIX_CODE_TEXT + f"{username}"
    old_code_info = redis_conn.client.get(code_key)
    if old_code_info is not None:
        return False

    code_info = json.dumps(code_info)
    redis_conn.client.set(code_key, code_info, ex=SIGNUP_CODE_EXPIRY)
    return True


def code_token_generated_saved(username):
    code = str(random.randint(SIGNUP_CODE_RANGE_MIN, SIGNUP_CODE_RANGE_MAX))
    token = uuid4().hex
    code_saved_in_redis = set_dict_in_redis(
        {"username": username, "code": code, "token": token}
    )

    if not code_saved_in_redis:
        return (
            False,
            "",
            "",
            Response(
                {"message": "بعد از گذشت ۵ دقیقه دوباره تلاش کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    return True, code, token, ""


def send_sms_code(to, code):
    send_sms = FeatureToggle.objects.filter(name=SEND_SIGNUP_SMS_STATUS).first()
    if send_sms.state == ACTIVE:
        MELIPAYAMAK_USERNAME = os.environ.setdefault(
            "MELIPAYAMAK_USERNAME", "09102188113"
        )
        MELIPAYAMAK_PASSOWRD = os.environ.setdefault("MELIPAYAMAK_PASSOWRD", "TL5OC")
        api = Api(MELIPAYAMAK_USERNAME, MELIPAYAMAK_PASSOWRD)
        sms = api.sms()
        response = sms.send_by_base_number(text=code, to=to, bodyId=263013)
        response = response.get("StrRetStatus")
    elif DEBUG:
        response = MELIPAYAMAK_OK_RESPONSE
    else:
        response = "NOK"

    return response


def get_dict_from_redis(username):
    code_key = REDIS_PREFIX_CODE_TEXT + f"{username}"
    code_info = redis_conn.client.get(code_key)
    return None if code_info is None else json.loads(code_info.decode("utf-8"))


def check_code_expiry(username):
    code_info = get_dict_from_redis(username)
    if code_info is None:
        return True, Response(
            {"message": "کد منقضی شده است، لطفا دوباره تلاش کنید"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return False, code_info


def check_token_match(generated_token, sent_token):
    if sent_token != generated_token:
        return False, Response(
            {"message": "درخواست نامعتبر"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return True, "OK"


def check_code_match(generated_code, sent_code):
    if sent_code != generated_code:
        return False, Response(
            {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
        )

    return True, "OK"


def password_is_valid(password):
    try:
        validate_password(password)
        return True
    except Exception as e:
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)
        return False


def create_new_user(request, username, password):
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


class SignUpAPIView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        username = persian_numbers_to_english(request.data.get("username"))

        passed_limit, result = check_daily_signup_limitation(request)
        if passed_limit:
            return result

        validated, result = is_valid_username(username)
        if not validated:
            return result

        generated, code, token, result = code_token_generated_saved(username)
        if not generated:
            return result

        response = send_sms_code(username, code)
        if response == MELIPAYAMAK_OK_RESPONSE:
            return Response(
                {"message": "کد تایید ارسال شد", "token": token},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": "متاسفانه کد ارسال نشد، بعد از چند دقیقه دوباره تلاش کنید و یا با پشتیبانی سایت تماس بگیرید"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request):
        username = str(request.data.get("username"))
        expired, result = check_code_expiry(username)
        if expired:
            return result

        generated_token = result.get("token")
        generated_code = result.get("code")

        sent_token = str(request.data.get("token"))
        matched, result = check_token_match(generated_token, sent_token)
        if not matched:
            return result

        sent_code = str(persian_numbers_to_english(request.data.get("code")))
        matched, result = check_code_match(generated_code, sent_code)
        if not matched:
            return result

        password = str(request.data.get("password"))
        return create_new_user(request, username, password)
