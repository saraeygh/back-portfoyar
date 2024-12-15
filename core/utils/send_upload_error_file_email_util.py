from django.core.mail import EmailMessage
from core.configs import EMAIL_TO


def send_upload_error_file_email(file_path: str, task_name: str) -> None:
    subject = f"نتیجه آپلود اطلاعات {task_name}"
    email_to = EMAIL_TO

    html_body = (
        "مواردی که در فایل سی‌اس‌وی پیوست آمده‌اند،"
        "به دلیل نداشتن قالب تعریف شده، در دیتابیس ثبت نشده‌اند."
        "لطفاً آن‌ها را اصلاح و مجدد آپلود کنید."
    )

    email = EmailMessage(
        subject=subject,
        body=html_body,
        to=[email_to],
    )

    email.attach_file(file_path)

    email.send()
