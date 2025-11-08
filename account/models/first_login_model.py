import jdatetime as jdt

from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin

from core.models import TimeStampMixin
from core.configs import TEHRAN_TZ, YYYY_MM_DD_HH_MM_SS


class FirstLogin(TimeStampMixin, models.Model):
    user = models.OneToOneField(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="first_login",
    )

    has_logged_in = models.BooleanField(verbose_name="لاگین‌اول؟", default=False)

    @property
    @admin.display(description="ایجاد")
    def created_at_shamsi(self):
        if not self.created_at:
            return "-"

        tehran_time = self.created_at.astimezone(TEHRAN_TZ)
        shamsi = jdt.datetime.fromgregorian(datetime=tehran_time)
        return shamsi.strftime(YYYY_MM_DD_HH_MM_SS)

    @property
    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self):
        if not self.updated_at:
            return "-"

        tehran_time = self.updated_at.astimezone(TEHRAN_TZ)
        shamsi = jdt.datetime.fromgregorian(datetime=tehran_time)
        return shamsi.strftime(YYYY_MM_DD_HH_MM_SS)

    class Meta:
        verbose_name = "لاگین اول"
        verbose_name_plural = "۷) لاگین‌های اول"
