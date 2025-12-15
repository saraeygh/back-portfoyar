from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle


from core.utils import SEND_SIGNUP_SMS, persian_numbers_to_english
from core.configs import (
    REDIS_SIGNUP_PREFIX,
    SMS_ONLINE_SUCCESS_STATUS,
    SIGNUP_CODE_EXPIRY,
)
from account.utils import (
    sms_online_send_sms,
    check_daily_limitation,
    is_valid_username,
    code_token_generated_saved,
    check_code_expiry,
    password_is_valid,
    check_token_match,
    check_code_match,
)


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

        passed_limit, result = check_daily_limitation(request)
        if passed_limit:
            return result

        validated, result = is_valid_username(username)
        if not validated:
            return result

        generated, code, token, result = code_token_generated_saved(
            username, REDIS_SIGNUP_PREFIX, SIGNUP_CODE_EXPIRY
        )
        if not generated:
            return result

        sms_text = (
            f"کاربر گرامی پرتفویار، کد تایید شما: {code}\n@my.portfoyar.com #{code}"
        )
        response = sms_online_send_sms([username], sms_text, SEND_SIGNUP_SMS["name"])
        if response == SMS_ONLINE_SUCCESS_STATUS:
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
        expired, response = check_code_expiry(username, REDIS_SIGNUP_PREFIX)
        if expired:
            return response

        generated_token = response.get("token")
        generated_code = response.get("code")

        sent_token = str(request.data.get("token"))
        matched, response = check_token_match(generated_token, sent_token)
        if not matched:
            return response

        sent_code = str(persian_numbers_to_english(request.data.get("code")))
        matched, response = check_code_match(generated_code, sent_code)
        if not matched:
            return response

        password = str(request.data.get("password"))
        return create_new_user(request, username, password)
