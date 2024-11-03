import json
import random

from django.contrib.auth.models import User


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes


from core.utils import RedisInterface, SEND_CHANGE_USERNAME_SMS
from core.configs import KEY_WITH_EX_REDIS_DB, CODE_RANGE_MIN, CODE_RANGE_MAX
from account.utils import send_sms_verify_code, is_valid_username

redis_conn = RedisInterface(db=KEY_WITH_EX_REDIS_DB)


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
        is_valid, result = is_valid_username(new_username)
        if not is_valid:
            return result

        username = request.user.username
        code = str(random.randint(CODE_RANGE_MIN, CODE_RANGE_MAX))
        code_saved_in_redis = set_dict_in_redis(
            {"username": username, "new_username": new_username, "code": code}
        )
        if not code_saved_in_redis:
            return Response(
                {"message": "بعد از گذشت ۵ دقیقه دوباره تلاش کنید"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = send_sms_verify_code(new_username, code, SEND_CHANGE_USERNAME_SMS)
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
