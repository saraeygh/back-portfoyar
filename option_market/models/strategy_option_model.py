from django.db import models
from core.models import TimeStampMixin

LIMITED_PROFIT = "limited_profit"
UNLIMITED_PROFIT = "unlimited_profit"
PROFIT_STATUS_CHOICES = [
    (LIMITED_PROFIT, "سود محدود"),
    (UNLIMITED_PROFIT, "سود نامحدود"),
]


NO_RISK = "no_risk"
LOW_RISK = "low_risk"
HIGH_RISK = "high_risk"
RISK_LEVEL_CHOICES = [
    (NO_RISK, "استراتژی‌های بدون ریسک"),
    (LOW_RISK, "استراتژی‌های با ریسک کم"),
    (HIGH_RISK, "استراتژی‌های با ریسک زیاد"),
]


PROFITS = {profit[0]: profit[1] for profit in PROFIT_STATUS_CHOICES}
RISKS = {risk[0]: risk[1] for risk in RISK_LEVEL_CHOICES}


class StrategyOption(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name="نام استراتژی", max_length=255)

    key = models.CharField(verbose_name="نام کلید", max_length=255)

    profit_status = models.CharField(
        verbose_name="وضعیت سوددهی",
        choices=PROFIT_STATUS_CHOICES,
        max_length=255,
        default="limited_profit",
    )

    risk_level = models.CharField(
        verbose_name="سطح ریسک",
        choices=RISK_LEVEL_CHOICES,
        max_length=255,
        default="no_risk",
    )

    sequence = models.IntegerField(verbose_name="ترتیب", default=1)

    desc = models.CharField(
        verbose_name="نحوه اجرای استراتژی", default="-", max_length=255
    )

    @property
    def profit(self):
        return PROFITS.get(self.profit_status, "")

    @property
    def risk(self):
        return RISKS.get(self.risk_level, "")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "استراتژی"
        verbose_name_plural = "۰۱) استراتژی‌ها"
