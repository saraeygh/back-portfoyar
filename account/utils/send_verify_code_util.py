import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.models import ACTIVE, FeatureToggle
from samaneh.settings import DEBUG

from core.configs import (
    MELIPAYAMAK_USERNAME,
    MELIPAYAMAK_PASSOWRD,
    PORTFOYAR_SMS_ID,
    MELIPAYAMAK_OK_RESPONSE,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
)

from melipayamak.melipayamak import Api

from colorama import Fore, Style


def send_sms_verify_code(to, code, sms_type):
    send_sms = FeatureToggle.objects.filter(name=sms_type).first()
    if send_sms.state == ACTIVE:
        api = Api(MELIPAYAMAK_USERNAME, MELIPAYAMAK_PASSOWRD)
        sms = api.sms()
        response = sms.send_by_base_number(text=code, to=to, bodyId=PORTFOYAR_SMS_ID)
        response = response.get("StrRetStatus")
    elif DEBUG:
        response = MELIPAYAMAK_OK_RESPONSE
    else:
        response = "NOK"

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
        print(Fore.RED + f"Error sending email: {e}" + Style.RESET_ALL)
        return False
