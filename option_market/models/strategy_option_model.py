from django.db import models
from core.models import TimeStampMixin

LIMITED_PROFIT = "limited_profit"
UNLIMITED_PROFIT = "unlimited_profit"
PROFIT_STATUS_CHOICES = [
    (LIMITED_PROFIT, "با سود محدود"),
    (UNLIMITED_PROFIT, "با سود نامحدود"),
]


NO_RISK = "no_risk"
LOW_RISK = "low_risk"
HIGH_RISK = "high_risk"
RISK_LEVEL_CHOICES = [
    (NO_RISK, "استراتژی‌های بدون ریسک"),
    (LOW_RISK, "استراتژی‌های با ریسک کم"),
    (HIGH_RISK, "استراتژی‌های با ریسک زیاد"),
]


class StrategyOption(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name="نام استراتژی", max_length=255)

    key = models.CharField(verbose_name="نام کلید", max_length=255)

    profit_status = models.CharField(
        verbose_name=("وضعیت سوددهی"),
        choices=PROFIT_STATUS_CHOICES,
        max_length=255,
        default="limited_profit",
    )

    risk_level = models.CharField(
        verbose_name=("سطح ریسک"),
        choices=RISK_LEVEL_CHOICES,
        max_length=255,
        default="no_risk",
    )

    sequence = models.IntegerField(verbose_name=("ترتیب"), default=1)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "استراتژی"
        verbose_name_plural = "۰۱) استراتژی‌ها"
