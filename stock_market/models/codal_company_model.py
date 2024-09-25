from core.models import TimeStampMixin
from django.db import models


ACCEPTED_IN_BOURSE = 0
ACCEPTED_IN_FARABOURSE = 1
REGISTERED_NOT_ACCEPTED = 2
NOT_REGISTERED = 3
ACCEPTED_IN_COMMODITY_MARKET = 4
ACCEPTED_IN_ENERGY_MARKET = 5

PUBLISHER_STATE_CHOICES = [
    (ACCEPTED_IN_BOURSE, "پذیرفته شده در بورس تهران"),
    (ACCEPTED_IN_FARABOURSE, "پذیرفته شده در فرابورس ایران"),
    (REGISTERED_NOT_ACCEPTED, "ثبت شده پذیرفته نشده"),
    (NOT_REGISTERED, "ثبت نشده نزد سازمان"),
    (ACCEPTED_IN_COMMODITY_MARKET, "پذیرفته شده در بورس کالای ایران"),
    (ACCEPTED_IN_ENERGY_MARKET, "پذیرفته شده دربورس انرژی ایران"),
]


class CodalCompany(TimeStampMixin, models.Model):
    symbol = models.CharField(
        verbose_name=("نماد"),
        max_length=255,
        unique=True,
    )
    codal_id = models.CharField(verbose_name=("آیدی کدال"), max_length=255)
    name = models.CharField(verbose_name=("نام شرکت"), max_length=255)

    publisher_state = models.IntegerField(
        verbose_name=("وضعیت ناشر"), choices=PUBLISHER_STATE_CHOICES
    )
    codal_t = models.IntegerField(verbose_name=("فیلد t"))

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = "شرکت کدال"
        verbose_name_plural = "۲۱) شرکت‌های کدال"
