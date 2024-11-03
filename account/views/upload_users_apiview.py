import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from samaneh.settings.common import BASE_DIR

from django.core.validators import validate_email
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from colorama import Fore, Style

from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
)


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except Exception:
        return False


@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
class UploadUsersAPIView(APIView):

    def post(self, request):
        try:
            users = pd.read_excel(
                io=request.FILES.get("users"),
                engine="openpyxl",
                dtype={
                    "username": object,
                    "password": object,
                    "email": object,
                    "first_name": object,
                    "last_name": object,
                },
            )

            users = users[["username", "password", "email", "first_name", "last_name"]]

        except (KeyError, ValueError):
            return Response(
                data={"message": "فایل اکسل مطابق الگو نیست"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        users = users.to_dict(orient="records")

        for user in users:
            not_valid_users = []
            username = user.get("username")
            password = user.get("password")
            email = user.get("email")
            first_name = user.get("first_name")
            last_name = user.get("last_name")

            user_obj: User = User.objects.filter(username=username)
            if user_obj.exists():
                print(Fore.RED + f"Existing user: [{username}]" + Style.RESET_ALL)
                continue
            else:
                new_user = User(username=username)
                if is_valid_email(email):
                    new_user.email = email
                if isinstance(first_name, str):
                    new_user.first_name = first_name
                if isinstance(last_name, str):
                    new_user.last_name = last_name

                new_user.set_password(password)
                new_user.save()
                print(Fore.GREEN + f"Created user: [{username}]" + Style.RESET_ALL)

        if not_valid_users:
            error_users_df = pd.DataFrame(not_valid_users)
            file_name = "error_users.xlsx"
            error_users_df.to_excel(
                excel_writer=f"{BASE_DIR}/media/uploaded_files/{file_name}",
                index=False,
                engine="openpyxl",
                sheet_name="error_users",
            )
            send_upload_excel_error_file_email(filename=file_name, task_name="کاربران")

        return Response({"message": "عملیات انجام شد."}, status=status.HTTP_200_OK)


# UPLOAD EXCEL FILES
def send_upload_excel_error_file_email(filename: str, task_name: str):
    subject = f"نتیجه آپلود اکسل اطلاعات {task_name}"

    html_body = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>

            <p style='direction: rtl; unicode-bidi: embed;'>
            نتیجه آپلود اکسل اطلاعات کاربران
            </p>

        </body>
        </html>
        """

    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["To"] = EMAIL_TO
    message["Subject"] = subject

    message.attach(MIMEText(html_body, "html", "utf-8"))

    filepath = f"{BASE_DIR}/media/uploaded_files/{filename}"

    with open(filepath, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)

    text = message.as_string()

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, EMAIL_TO, text)
    except Exception as e:
        print(Fore.RED + f"Error sending email: {e}" + Style.RESET_ALL)

    try:
        os.remove(filepath)
    except Exception:
        print(Fore.RED + f"Error removing file: {e}" + Style.RESET_ALL)
