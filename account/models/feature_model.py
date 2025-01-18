import pytz
from datetime import datetime

import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.db import models
from django.contrib import admin
from core.models import TimeStampMixin


ALL_FEATURE = "all_feature"
OPTION_FEATURE = "option_feature"
DOMESTIC_FEATURE = "domestic_feature"
FUTURE_FEATURE = "future_feature"
GLOBAL_FEATURE = "global_feature"
STOCK_FEATURE = "stock_feature"
SUBSCRIPTION_FEATURE_CHOICES = [
    (ALL_FEATURE, "تمام قابلیت‌های سایت"),
    (DOMESTIC_FEATURE, "بخش بورس کالای داخلی"),
    (FUTURE_FEATURE, "بخش ابزارهای مشتقه بورس کالا"),
    (GLOBAL_FEATURE, "بخش بازارهای جهانی"),
    (OPTION_FEATURE, "بخش آپشن‌ها"),
    (STOCK_FEATURE, "بخش تابلوخوانی"),
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

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)

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

    login_count = models.IntegerField(verbose_name="تعداد کاربران", default=1)

    @property
    @admin.display(description="قیمت با تخفیف")
    def discounted_price(self):
        if self.has_discount:
            price = int(self.price * (1 - (self.discount_percent / 100)))
            return price
        else:
            return self.price

    def __str__(self) -> str:
        return f"{self.name} - {self.duration}"

    class Meta:
        verbose_name = "قابلیت سایت (فعال)"
        verbose_name_plural = "۲)  (فعال) قابلیت‌های سایت"


class DisabledFeature(Feature):
    class Meta:
        proxy = True
        verbose_name = "قابلیت سایت (غیرفعال)"
        verbose_name_plural = "۲) قابلیت‌های سایت (غیرفعال)"


class FeatureDiscount(TimeStampMixin, models.Model):

    feature = models.ForeignKey(
        verbose_name="قابلیت سایت",
        to=Feature,
        on_delete=models.CASCADE,
        related_name="discounts",
    )

    name = models.CharField(
        verbose_name="نام تخفیف", max_length=255, default="", blank=True
    )

    description = models.TextField(verbose_name="توضیحات تخفیف", default="", blank=True)

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)

    discount_percent = models.IntegerField(verbose_name="میزان تخفیف", default=0)

    has_discount_code = models.BooleanField(
        verbose_name="کد تخفیف دارد؟", default=False
    )
    discount_code = models.CharField(verbose_name="کد تخفیف", default="", blank=True)

    has_start = models.BooleanField(verbose_name="تاریخ شروع دارد؟", default=False)
    start_at = models.DateTimeField(verbose_name="زمان شروع", default=datetime.now)

    has_expiry = models.BooleanField(verbose_name="تاریخ پایان دارد؟", default=False)
    expire_at = models.DateTimeField(verbose_name="زمان پایان", default=datetime.now)

    has_max_use_count = models.BooleanField(
        verbose_name="محدودیت دفعات استفاده", default=False
    )
    used_count = models.IntegerField(verbose_name="دفعات استفاده شده", default=0)
    max_use_count = models.IntegerField(
        verbose_name="محدودیت دفعات استفاده", default=1000
    )

    @admin.display(description="تاریخ شروع")
    def start_at_shamsi(self):
        shamsi = (
            JalaliDateTime(self.start_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")
        return shamsi

    @admin.display(description="تاریخ پایان")
    def expire_at_shamsi(self):
        shamsi = (
            JalaliDateTime(self.expire_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")
        return shamsi

    def __str__(self) -> str:
        return f"{self.name} - {self.feature.name} - {self.feature.duration}"

    class Meta:
        verbose_name = " (فعال) تخفیف قابلیت سایت"
        verbose_name_plural = "۳) (فعال) تخفیف‌های قابلیت‌های سایت"


class DisabledFeatureDiscount(FeatureDiscount):
    class Meta:
        proxy = True
        verbose_name = "تخفیف قابلیت سایت (غیرفعال)"
        verbose_name_plural = "۳) تخفیف‌های قابلیت‌های سایت (غیرفعال)"
