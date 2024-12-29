import traceback
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from colorama import Fore, Style

from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
)

SUCCESS_BODY = "SUCCESS"


def get_exception_detail(exception):
    if exception == SUCCESS_BODY:
        return exception

    exception_details = "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )
    return exception_details


def send_task_fail_success_email(task_name: str = "", exception: str = "SUCCESS"):
    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["To"] = EMAIL_TO
    message["Subject"] = task_name

    html_body = get_exception_detail(exception)
    message.attach(MIMEText(html_body, "html", "utf-8"))
    text = message.as_string()

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(from_addr=EMAIL_HOST_USER, to_addrs=EMAIL_TO, msg=text)
    except Exception as e:
        print(Fore.RED + f"Error sending email: {e}" + Style.RESET_ALL)
