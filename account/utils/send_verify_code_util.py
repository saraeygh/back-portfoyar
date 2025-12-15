import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from celery import shared_task

from zeep import Client

from samaneh.settings import DEBUG

from core.models import ACTIVE, FeatureToggle
from core.configs import (
    EMAIL_TO,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    SMS_ONLINE_WEB_SERVICE_URL,
    SMS_ONLINE_SENDER,
    SMS_ONLINE_USERNAME,
    SMS_ONLINE_PASSWORD,
    SMS_ONLINE_SUCCESS_STATUS,
)


def sms_online_send_sms(to, text, sms_type):
    send_sms = FeatureToggle.objects.filter(name=sms_type).first()

    params = {
        "username": SMS_ONLINE_USERNAME,
        "password": SMS_ONLINE_PASSWORD,
        "from": SMS_ONLINE_SENDER,
        "to": to,
        "text": text,
        "udh": "",
        "isflash": False,
        "recId": [],
        "status": [],
    }

    if send_sms.state == ACTIVE:
        try:
            client = Client(wsdl=SMS_ONLINE_WEB_SERVICE_URL)

            response = client.service.SendSms(**params)
            response = response["SendSmsResult"]

        except Exception as e:
            send_sms_fail_email.delay(to=str(to), text=text, exc=str(e))
            response = 1000

    elif DEBUG:
        response = SMS_ONLINE_SUCCESS_STATUS
    else:
        response = 1001

    return response


def send_email_verify_code(username: str, email: str, code: str):
    try:
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
        message["From"] = EMAIL_HOST_USER
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html", "utf-8"))

        text = message.as_string()
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, email, text)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@shared_task
def send_sms_fail_email(to: str, text: str, exc: str):
    try:
        subject = "مشکل در ارسال پیامک پرتفویار"

        html_body = f"""
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body>

                <p style='direction: rtl; unicode-bidi: embed;'>
                گیرنده‌ها:
                </p>

                <p style='direction: rtl; unicode-bidi: embed;'>
                {to}
                </p>

                <p style='direction: rtl; unicode-bidi: embed;'>
                متن پیام:
                </p>

                <p style='direction: rtl; unicode-bidi: embed;'>
                {text}
                </p>

                <p style='direction: rtl; unicode-bidi: embed;'>
                خطا:
                </p>

                <p style='direction: rtl; unicode-bidi: embed;'>
                {exc}
                </p>

            </body>
            </html>
            """

        message = MIMEMultipart()
        message["From"] = EMAIL_HOST_USER
        message["To"] = EMAIL_TO
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html", "utf-8"))

        text = message.as_string()
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, EMAIL_TO, text)
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False
