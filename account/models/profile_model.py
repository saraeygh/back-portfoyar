from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator


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

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "۱) پروفایل‌ها"
