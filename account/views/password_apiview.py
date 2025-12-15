from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import AnonRateThrottle
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authtoken.models import Token

from core.utils import (
    SEND_RESET_PASSWORD_SMS,
    persian_numbers_to_english,
)

from core.configs import (
    REDIS_RESET_PASSWORD_PREFIX,
    RESET_PASSWORD_CODE_EXPIRY,
    SMS_ONLINE_SUCCESS_STATUS,
)

from account.utils import (
    check_daily_limitation,
    sms_online_send_sms,
    code_token_generated_saved,
    check_code_expiry,
    check_token_match,
    check_code_match,
    is_valid_phone,
    password_is_valid,
)


def change_user_password(user, new_password):
    user.set_password(new_password)
    user.save()


def delete_user_token(user):
    Token.objects.filter(user=user).delete()


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PasswordAPIView(APIView):
    def put(self, request):
        OLD_PASSWORD = "old_password"
        NEW_PASSWORD = "new_password"
        errors = dict()

        user = request.user
        old_password = request.data.get(OLD_PASSWORD)
        new_password = request.data.get(NEW_PASSWORD)

        authenticated_user = authenticate(
            request=request, username=user.username, password=old_password
        )
        if authenticated_user is None:
            errors[OLD_PASSWORD] = "رمز عبور فعلی اشتباه است"

        if not password_is_valid(new_password):
            errors[NEW_PASSWORD] = "رمز عبور جدید قابل قبول نیست"

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if old_password == new_password:
            errors[OLD_PASSWORD] = "رمز عبور فعلی و جدید نمی‌توانند یکسان باشند"
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        change_user_password(user, new_password)
        delete_user_token(user)
        return Response(
            {"message": "رمز عبور با موفقیت تغییر پیدا کرد، لطفاً دوباره وارد شوید"},
            status=status.HTTP_200_OK,
        )


###############################################################################
def is_valid_username(username):
    user_exists = User.objects.filter(username=username).exists()
    if username is not None and is_valid_phone(username) and user_exists:
        return True, ""
    return False, Response(
        {"message": "امکان بازنشانی رمز عبور برای این نام کاربری وجود ندارد"},
        status=status.HTTP_400_BAD_REQUEST,
    )


def reset_user_password(request, username, password):
    if not password_is_valid(password):
        return Response(
            {
                "message": "رمز عبور انتخابی امن نیست، لطفاً یک رمز عبور قوی‌تر انتخاب کنید"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()

    authenticated_user = authenticate(
        request=request, username=username, password=password
    )
    if authenticated_user is None:
        return Response(
            {"message": "مشکلی پیش آمده است، با پشتیبانی تماس بگیرید"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": "رمز عبور حساب کاربری شما با موفقیت تغییر یافت"},
        status=status.HTTP_200_OK,
    )


class ResetPasswordAPIView(APIView):
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
            username, REDIS_RESET_PASSWORD_PREFIX, RESET_PASSWORD_CODE_EXPIRY
        )
        if not generated:
            return result

        sms_text = f"کد تایید پرتفویار \n {code}"
        response = sms_online_send_sms(
            [username], sms_text, SEND_RESET_PASSWORD_SMS["name"]
        )
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
        expired, response = check_code_expiry(username, REDIS_RESET_PASSWORD_PREFIX)
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
        return reset_user_password(request, username, password)
