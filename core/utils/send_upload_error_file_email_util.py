import os
import smtplib


from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
)


def send_upload_error_file_email(file_path: str, task_name: str, filename: str):
    subject = f"نتیجه آپلود اکسل اطلاعات {task_name}"

    html_body = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>
            <p style='direction: rtl; unicode-bidi: embed;'>
            "مواردی که در فایل سی‌اس‌وی پیوست آمده‌اند،"
            "به دلیل نداشتن قالب تعریف شده، در دیتابیس ثبت نشده‌اند."
            "لطفاً آن‌ها را اصلاح و مجدد آپلود کنید."
            </p>
        </body>
        </html>
        """

    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["To"] = EMAIL_TO
    message["Subject"] = subject

    message.attach(MIMEText(html_body, "html", "utf-8"))

    with open(file_path, "rb") as attachment:
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
        print(f"Error sending email: {e}")

    try:
        os.remove(file_path)
    except Exception:
        print(f"Error removing file: {e}")
