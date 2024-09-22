from django.db import models
from core.models import TimeStampMixin


class StrategyOption(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name="نام استراتژی", max_length=255)

    key = models.CharField(verbose_name="نام کلید", max_length=255)

    PROFIT_STATUS_CHOICES = [
        ("limited_profit", "با سود محدود"),
        ("unlimited_profit", "با سود نامحدود"),
    ]
    profit_status = models.CharField(
        verbose_name=("وضعیت سوددهی"),
        choices=PROFIT_STATUS_CHOICES,
        max_length=255,
        default="limited_profit",
    )

    RISK_LEVEL_CHOICES = [
        ("no_risk", "استراتژی‌های بدون ریسک"),
        ("low_risk", "استراتژی‌های با ریسک کم"),
        ("high_risk", "استراتژی‌های با ریسک زیاد"),
    ]
    risk_level = models.CharField(
        verbose_name=("سطح ریسک"),
        choices=RISK_LEVEL_CHOICES,
        max_length=255,
        default="no_risk",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "استراتژی"
        verbose_name_plural = "۰۱) استراتژی‌ها (جدید)"
