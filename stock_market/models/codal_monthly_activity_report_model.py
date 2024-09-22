from core.models import TimeStampMixin
from django.db import models
from . import CodalCompany


class CodalMonthlyActivityReport(TimeStampMixin, models.Model):

    company = models.ForeignKey(
        CodalCompany,
        on_delete=models.CASCADE,
        related_name="stock_monthly_activity",
    )

    tracing_number = models.IntegerField(verbose_name=("کد رهگیری"), unique=True)

    under_supervision = models.IntegerField(verbose_name=("تحت نظارت"))

    title = models.CharField(verbose_name=("عنوان"), max_length=255)

    code = models.CharField(verbose_name=("کد"), max_length=255)

    sent_date_time = models.DateTimeField(
        verbose_name="زمان ارسال", auto_now=False, auto_now_add=False
    )

    publish_date_time = models.DateTimeField(
        verbose_name="زمان انتشار", auto_now=False, auto_now_add=False
    )

    has_html = models.BooleanField(verbose_name="اچ‌تی‌ام‌ال")

    is_estimate = models.BooleanField(verbose_name="تقریبی")

    url = models.CharField(verbose_name=("آدرس"), max_length=255)

    has_excel = models.BooleanField(verbose_name="اکسل")

    has_pdf = models.BooleanField(verbose_name="پی‌دی‌اف")

    has_xbrl = models.BooleanField(verbose_name="ایکس بی آر ال")

    has_attachment = models.BooleanField(verbose_name="پیوست")

    attachment_url = models.CharField(verbose_name=("آدرس پیوست"), max_length=255)

    pdf_url = models.CharField(verbose_name=("آدرس پی‌دی‌اف"), max_length=255)

    excel_url = models.CharField(verbose_name=("آدرس اکسل"), max_length=255)

    xbrl_url = models.CharField(verbose_name=("آدرس ایکس‌بی‌آرال"), max_length=255)

    supervision = models.TextField(verbose_name=("نظارت"))

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "گزارش‌ فعالیت ماهانه"
        verbose_name_plural = "۲۲) گزارش‌های فعالیت‌ ماهانه"
