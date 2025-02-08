from threading import Thread
import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import pandas as pd
import jdatetime as jdt
import matplotlib.pyplot as plt

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from samaneh.settings import BASE_DIR

from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
)

from account.models import Profile


def convert_to_jalali(row):
    created_at = row.get("created_at")
    created_at = jdt.datetime.fromgregorian(datetime=created_at)
    created_at = created_at.date().strftime("%Y/%m/%d")

    return created_at


class NewUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        FILENAME = "new_users.jpg"
        users = pd.DataFrame(
            Profile.objects.values("user__username", "created_at", "note")
        )
        new_users = users["created_at"].dt.date.value_counts().reset_index()
        new_users["created_at"] = new_users.apply(convert_to_jalali, axis=1)

        plt.figure(figsize=(8, 5))
        plt.bar(
            new_users["created_at"].astype(str), new_users["count"], color="skyblue"
        )

        plt.xlabel("تاریخ")
        plt.ylabel("تعداد ثبت‌نام‌ها")
        plt.title("تعداد کاربران ثبت‌نامی بر حسب تاریخ ثبت‌نام")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        plt.savefig(FILENAME, format="jpg", dpi=300, bbox_inches="tight")
        plt.close()

        email_thread = Thread(
            target=send_email_with_attachment, args=(FILENAME, "آمار کاربران")
        )
        email_thread.start()

        return Response({"message": "DAWWSHHAAMMI"}, status=status.HTTP_200_OK)


def send_email_with_attachment(filename: str, task_name: str):
    email_host = EMAIL_HOST
    email_port = EMAIL_PORT
    email_host_user = EMAIL_HOST_USER
    email_host_password = EMAIL_HOST_PASSWORD
    email_to = EMAIL_TO

    subject = f"ایمیل {task_name}"

    html_body = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>

            <p style='direction: rtl; unicode-bidi: embed;'>
            آمار ثبت‌نام کاربران
            </p>

        </body>
        </html>
        """

    message = MIMEMultipart()
    message["From"] = email_host_user
    message["To"] = email_to
    message["Subject"] = subject

    message.attach(MIMEText(html_body, "html", "utf-8"))

    filepath = f"{BASE_DIR}/{filename}"

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
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_host_user, email_host_password)
            server.sendmail(email_host_user, email_to, text)
    except Exception as e:
        print(f"Error sending email: {e}")

    try:
        os.remove(filepath)
    except Exception:
        print(f"Error removing file: {e}")
