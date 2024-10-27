from datetime import datetime
from persiantools.jdatetime import JalaliDate

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

    start_at = models.DateField(verbose_name="تاریخ شروع اشتراک")
    end_at = models.DateField(verbose_name="تاریخ پایان اشتراک")

    @property
    @admin.display(boolean=True, description="فعال")
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
        verbose_name_plural = "۳) اشتراک‌ها"
