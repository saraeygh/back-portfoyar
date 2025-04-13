import pytz
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.contrib import admin


import jdatetime
from persiantools.jdatetime import JalaliDateTime

from core.models import TimeStampMixin


PHONE_PATTERN_REGEX = r"^09(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|7[0-9]|8[0-9]|9[0-9])-?[0-9]{3}-?[0-9]{4}$"
PHONE_PATTERN_MESSAGE = "شماره موبایل نامعتبر است"
PHONE_PATTERN_CODE = "invalid_phone"

MALE_GENDER = "m"
FEMALE_GENDER = "f"
GENDER_CHOICES = [(MALE_GENDER, "مرد"), (FEMALE_GENDER, "زن")]


class Profile(TimeStampMixin, models.Model):
    user = models.OneToOneField(
        verbose_name="کاربر", to=User, on_delete=models.CASCADE, related_name="profile"
    )

    max_login = models.IntegerField(verbose_name="حداکثر لاگین همزمان", default=1)
    active_login = models.IntegerField(verbose_name="لاگین‌های همزمان", default=0)

    phone = models.CharField(
        verbose_name="شماره موبایل",
        max_length=11,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=PHONE_PATTERN_REGEX,
                message=PHONE_PATTERN_MESSAGE,
                code=PHONE_PATTERN_CODE,
            )
        ],
    )

    gender = models.CharField(
        verbose_name="جنسیت",
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )

    birth_date = models.DateField(verbose_name="تاریخ تولد", blank=True, null=True)

    note = models.CharField(verbose_name="توضیحات", max_length=32, default="-")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self):
        shamsi = (
            JalaliDateTime(self.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self):
        shamsi = (
            JalaliDateTime(self.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "۱) پروفایل‌ها"


class LoginCount(TimeStampMixin, models.Model):
    user = models.OneToOneField(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="logincount",
    )

    count = models.IntegerField(verbose_name="تعداد لاگین", default=1)

    note = models.CharField(verbose_name="توضیحات", max_length=32, default="-")

    @admin.display(description="نام")
    def first_name(self):
        return self.user.first_name

    @admin.display(description="نام خانوادگی")
    def last_name(self):
        return self.user.last_name

    @admin.display(description="ایجاد")
    def created_at_shamsi(self):
        shamsi = (
            JalaliDateTime(self.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self):
        shamsi = (
            JalaliDateTime(self.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    class Meta:
        verbose_name = "تعداد لاگین"
        verbose_name_plural = "۶) تعداد لاگین‌ها"
