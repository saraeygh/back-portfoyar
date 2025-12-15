import os
import threading
import traceback
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


import jdatetime


from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
    TEHRAN_TZ,
)


BLUE = "BLUE"
GREEN = "GREEN"
RED = "RED"


def print_task_info(color: str = BLUE, name: str = ""):
    now = f"⏰ [{jdatetime.datetime.now(tz=TEHRAN_TZ).strftime("%Y/%m/%d %H:%M:%S")}]"
    if color == GREEN:
        print(now + " - " + name + " - Done")
    elif color == RED:
        print(now + " - " + name + " - ERROR")
    else:
        print(now + " - " + name + " - Running")

    return


SERVERS = {
    "LOCAL": "178.252.141.50",
    "TEST": "185.105.185.188",
    "PROD": "188.121.98.119",
}


def get_host():
    SERVER_NAME = os.environ.get("SERVER_NAME")
    host_name = SERVER_NAME or "NO_NAME"
    host_ip = SERVERS.get(SERVER_NAME) or "NO_IP"

    return host_name, host_ip


SUCCESS = "SUCCESS"
ERROR = "ERROR"


def get_task_result_status(exception):
    status = SUCCESS
    if exception != SUCCESS:
        status = ERROR

    return status


def get_exception_detail(exception, host_name, host_ip):

    if exception == SUCCESS:
        exception_details = exception
    else:
        exception_details = "".join(
            traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        )

    return host_name + f"({host_ip})" + ": " + exception_details


def send_task_fail_success_email(task_name: str = "", exception: str = SUCCESS):
    host_name, host_ip = get_host()
    status = get_task_result_status(exception)

    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["To"] = EMAIL_TO
    message["Subject"] = "POR" + f" ({host_name}) - " + status + task_name

    html_body = get_exception_detail(exception, host_name, host_ip)
    message.attach(MIMEText(html_body, "html", "utf-8"))
    text = message.as_string()

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(from_addr=EMAIL_HOST_USER, to_addrs=EMAIL_TO, msg=text)
    except Exception as e:
        print(f"Error sending email: {e}")


def send_exception_detail_email(task_name, exception):
    print(f"{exception}")
    send_email_thread = threading.Thread(
        target=send_task_fail_success_email,
        kwargs={"task_name": task_name, "exception": exception},
    )
    send_email_thread.start()


def run_main_task(main_task, kw_args: dict = {}, daily: bool = False):
    TASK_NAME = main_task.__name__
    print_task_info(name=TASK_NAME)

    try:
        main_task(**kw_args)
        if daily:
            send_email_thread = threading.Thread(
                target=send_task_fail_success_email,
                kwargs={"task_name": TASK_NAME},
            )
            send_email_thread.start()
        print_task_info(color="GREEN", name=TASK_NAME)

    except Exception as e:
        send_exception_detail_email(TASK_NAME, e)
