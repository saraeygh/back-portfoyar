import pytz
import jdatetime

from datetime import datetime
from persiantools.jdatetime import JalaliDateTime, JalaliDate

from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin

from core.models import TimeStampMixin

from . import Feature


class Subscription(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="subscription",
    )

    feature = models.ForeignKey(
        verbose_name="قابلیت سایت",
        to=Feature,
        on_delete=models.CASCADE,
        related_name="subscription",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=True)

    start_at = models.DateField(verbose_name="تاریخ شروع اشتراک")
    end_at = models.DateField(verbose_name="تاریخ پایان اشتراک")

    @property
    @admin.display(boolean=True, description="اعتبار دارد؟")
    def is_active(self):
        today_date = datetime.today().date()
        sub_end_date = self.end_at
        if (sub_end_date - today_date).days >= 0:
            return True
        else:
            return False

    @admin.display(description="روزهای باقیمانده")
    def remained_days(self):
        today_date = datetime.today().date()
        sub_end_date = self.end_at
        remained_days = (sub_end_date - today_date).days
        if remained_days >= 0:
            return remained_days
        else:
            return 0

    @admin.display(description="تاریخ شروع")
    def start_at_shamsi(self):
        shamsi = JalaliDate(self.start_at).strftime("%Y-%m-%d")
        return shamsi

    @admin.display(description="تاریخ پایان")
    def end_at_shamsi(self):
        shamsi = JalaliDate(self.end_at).strftime("%Y-%m-%d")
        return shamsi

    class Meta:
        verbose_name = "اشتراک"
        verbose_name_plural = "۵) اشتراک‌ها"


class UserDiscount(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="discounts",
    )

    feature = models.ForeignKey(
        verbose_name="قابلیت سایت",
        to=Feature,
        on_delete=models.CASCADE,
        related_name="user_discounts",
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
    max_use_count = models.IntegerField(verbose_name="محدودیت دفعات استفاده", default=1)

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
        verbose_name = "تخفیف کاربر"
        verbose_name_plural = "۴) تخفیف‌های کاربران"
