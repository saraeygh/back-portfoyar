import os
import json
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.core.validators import validate_email

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.utils import RedisInterface

redis_conn = RedisInterface(db=1)


def send_email_verification_code(username: str, email: str, code: str):
    try:
        email_host = os.environ.setdefault("EMAIL_HOST", "smtp.gmail.com")
        email_port = os.environ.setdefault("EMAIL_PORT", "587")
        email_host_user = os.environ.setdefault(
            "EMAIL_HOST_USER", "armansmtptest@gmail.com"
        )
        email_host_password = os.environ.setdefault(
            "EMAIL_HOST_PASSWORD", "gaux sxiy zhyf qhdx"
        )
        email_to = email

        subject = f"کد تایید ایمیل پرتفویار برای حساب {username}"

        html_body = f"""
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body>

                <p style='direction: rtl; unicode-bidi: embed;'>
                کد تایید شما برای ایمیل سامانه پرتفویار:
                </p>

                <p style='direction: rtl; unicode-bidi: embed;'>
                {code}
                </p>

            </body>
            </html>
            """

        message = MIMEMultipart()
        message["From"] = email_host_user
        message["To"] = email_to
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html", "utf-8"))

        text = message.as_string()
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, email_to, text)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except Exception:
        return False


def set_dict_in_redis(code_info: dict):
    username = code_info.get("username")
    code_info = json.dumps(code_info)

    code_key = f"email_verify_code_{username}"
    expiration_time = 60 * 5
    redis_conn.client.delete(code_key)
    redis_conn.client.set(code_key, code_info, ex=expiration_time)


def get_dict_from_redis(username):
    code_key = f"email_verify_code_{username}"
    code_info = redis_conn.client.get(code_key)
    return None if code_info is None else json.loads(code_info.decode("utf-8"))


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class EmailAPIView(APIView):
    def get(self, request):
        email = {"email": request.user.email}
        return Response(email, status=status.HTTP_200_OK)

    def post(self, request):
        email = request.data.get("email")
        if email is None or not is_valid_email(email):
            return Response(
                {"message": "ایمیل نامعتبر"}, status=status.HTTP_400_BAD_REQUEST
            )

        username = request.user.username
        code = str(random.randint(123456, 999999))
        set_dict_in_redis({"username": username, "email": email, "code": code})
        sent = send_email_verification_code(username, email, code)
        if sent:
            return Response(
                {"message": "ایمیل کد تایید ارسال شد"}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": "متاسفانه ایمیل ارسال نشد، دوباره تلاش کنید"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request):
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
            return Response(
                {"message": "ایمیل به‌روزرسانی شد"}, status=status.HTTP_200_OK
            )

        return Response(
            {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
        )
