from datetime import datetime

from django.db import models
from django.contrib import admin
from core.models import TimeStampMixin


ALL_FEATURE = "all_feature"
SUBSCRIPTION_FEATURE_CHOICES = [
    (ALL_FEATURE, "تمام قابلیت‌ها"),
]

ONE_MONTH = 1
THREE_MONTH = 3
SIX_MONTH = 6
TWELVE_MONTH = 12
FEATURE_DURATION_CHOICES = [
    (ONE_MONTH, "۱ ماه"),
    (THREE_MONTH, "۳ ماه"),
    (SIX_MONTH, "۶ ماه"),
    (TWELVE_MONTH, "۱۲ ماه"),
]


class Feature(TimeStampMixin, models.Model):

    name = models.CharField(
        verbose_name="قابلیت سایت",
        max_length=32,
        choices=SUBSCRIPTION_FEATURE_CHOICES,
    )

    duration = models.IntegerField(
        verbose_name="مدت زمان",
        choices=FEATURE_DURATION_CHOICES,
    )

    price = models.BigIntegerField(verbose_name="قیمت")

    has_discount = models.BooleanField(verbose_name="تخفیف", default=False)
    discount_percent = models.IntegerField(verbose_name="میزان تخفیف", default=0)

    @property
    @admin.display(description="قیمت با تخفیف")
    def discounted_price(self):
        if self.has_discount:
            price = (100 - self.discount_percent) / 100
            price = int(self.price * price)
            return price
        else:
            return self.price

    def __str__(self) -> str:
        return f"{self.name} - {self.duration}"

    class Meta:
        verbose_name = "قابلیت سایت"
        verbose_name_plural = "۲) قابلیت‌های سایت"
