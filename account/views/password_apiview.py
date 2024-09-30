import os
import re
import json
import smtplib
import random

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes


from core.utils import RedisInterface

redis_conn = RedisInterface(db=1)


def password_is_valid(password):
    try:
        validate_password(password)
        return True
    except Exception as e:
        print(e)
        return False


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PasswordAPIView(APIView):
    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        authenticated_user = authenticate(
            request=request, username=user.username, password=old_password
        )
        if authenticated_user is None:
            return Response(
                {"message": "رمز عبور قبلی اشتباه است"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password_is_valid(new_password):
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "رمز عبور با موفقیت تغییر کرد"}, status=status.HTTP_200_OK
            )

        return Response(
            {"message": "رمز عبور جدید قابل قبول نیست"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # def post(self, request):
    #     new_username = request.data.get("username")
    #     user_exists = User.objects.filter(username=new_username).exists()
    #     if new_username is None or not is_valid_phone(new_username) or user_exists:
    #         return Response(
    #             {"message": "شماره موبایل نامعتبر"}, status=status.HTTP_400_BAD_REQUEST
    #         )

    #     username = request.user.username
    #     code = str(random.randint(123456, 999999))
    #     code_saved_in_redis = set_dict_in_redis(
    #         {"username": username, "new_username": new_username, "code": code}
    #     )
    #     if not code_saved_in_redis:
    #         return Response(
    #             {"message": "بعد از گذشت ۵ دقیقه دوباره تلاش کنید"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     response = send_sms_code(new_username, code)
    #     if response == "Ok":
    #         return Response({"message": "کد تایید ارسال شد"}, status=status.HTTP_200_OK)
    #     return Response(
    #         {"message": "متاسفانه کد ارسال نشد، بعد از ۵ دقیقه دوباره تلاش کنید"},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    # def patch(self, request):
    #     sent_code = str(request.data.get("code"))
    #     user: User = request.user
    #     code_info = get_dict_from_redis(user.username)
    #     if code_info is None:
    #         return Response(
    #             {"message": "کد منقضی شده است، لطفا دوباره تلاش کنید"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #     generated_code = code_info.get("code")
    #     if sent_code == generated_code:
    #         new_username = code_info.get("new_username")
    #         user.username = new_username
    #         user.save()
    #         return Response(
    #             {"message": "نام کاربری به‌روزرسانی شد"}, status=status.HTTP_200_OK
    #         )

    #     return Response(
    #         {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
    #     )
