import smtplib
import threading

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


from django.db.models.signals import post_save
from django.dispatch import receiver

from core.configs import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_TO,
)

from support.models import Ticket, TicketResponse
from support.views import TICKET_APPENDIX_FILES_DIR

from colorama import Fore, Style


RECIPIENTS = [
    EMAIL_TO,
]


@receiver(post_save, sender=TicketResponse)
def send_new_ticket_response_email(sender, instance: TicketResponse, created, **kwargs):
    if created:
        sender_user = instance.user.username
        receiver_user = (
            f"پاسخ به تیکت شماره {instance.ticket.id}" + " - " + instance.ticket.title
        )
        title = instance.text
        file_name = instance.file
        if file_name:
            file_path = f"{TICKET_APPENDIX_FILES_DIR}{file_name}"
        else:
            file_name = None
            file_path = None

        subject = "پاسخ تیکت جدید"
        send_email_thread = threading.Thread(
            target=send_email,
            args=(subject, sender_user, receiver_user, title, file_name, file_path),
        )
        send_email_thread.start()


@receiver(post_save, sender=Ticket)
def send_new_ticket_email(sender, instance: Ticket, created, **kwargs):
    if created:
        sender_user = instance.sender_user.username
        receiver_user = instance.receiver_user.username
        title = instance.title
        file_name = instance.file
        if file_name:
            file_path = f"{TICKET_APPENDIX_FILES_DIR}{file_name}"
        else:
            file_name = None
            file_path = None

        subject = "تیکت جدید"
        send_email_thread = threading.Thread(
            target=send_email,
            args=(subject, sender_user, receiver_user, title, file_name, file_path),
        )
        send_email_thread.start()


def send_email(
    subject: str = "",
    sender_user: str = "",
    receiver_user: str = "",
    title: str = "",
    file_name: str = None,
    file_path: str = None,
):
    file_url = "ندارد"
    if file_name:
        file_url = f"https://portfoyar.com/api/support/appendix/{file_name}/"

    html_body = f"""
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>

            <p style='direction: rtl; unicode-bidi: embed;'>
            فرستنده: {sender_user}
            </p>

            <p style='direction: rtl; unicode-bidi: embed;'>
            گیرنده: {receiver_user}
            </p>

            <p style='direction: rtl; unicode-bidi: embed;'>
            عنوان تیکت یا متن پاسخ: {title}
            </p>

            <p style='direction: rtl; unicode-bidi: embed;'>
            ضمیمه: {file_url}
            </p>

        </body>
        </html>
        """

    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["To"] = EMAIL_TO
    message["Subject"] = subject

    message.attach(MIMEText(html_body, "html", "utf-8"))

    if file_path:
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_name}",
        )

        message.attach(part)

    text = message.as_string()

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(
                from_addr=EMAIL_HOST_USER,
                to_addrs=RECIPIENTS,
                msg=text,
            )
    except Exception as e:
        print(Fore.RED + f"Error sending email: {e}" + Style.RESET_ALL)
