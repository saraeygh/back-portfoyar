from core.models import TimeStampMixin
from django.db import models


class CodalCompany(TimeStampMixin, models.Model):
    symbol = models.CharField(
        verbose_name=("نماد"),
        max_length=255,
        unique=True,
    )
    codal_id = models.CharField(verbose_name=("آیدی کدال"), max_length=255)
    name = models.CharField(verbose_name=("نام شرکت"), max_length=255)

    PUBLISHER_STATE_CHOICES = [
        (0, "پذیرفته شده در بورس تهران"),
        (1, "پذیرفته شده در فرابورس ایران"),
        (2, "ثبت شده پذیرفته نشده"),
        (3, "ثبت نشده نزد سازمان"),
        (4, "پذیرفته شده در بورس کالای ایران"),
        (5, "پذیرفته شده دربورس انرژی ایران"),
    ]

    publisher_state = models.IntegerField(
        verbose_name=("وضعیت ناشر"), choices=PUBLISHER_STATE_CHOICES
    )
    codal_t = models.IntegerField(verbose_name=("فیلد t"))

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = "شرکت کدال"
        verbose_name_plural = "۲۱) شرکت‌های کدال"
