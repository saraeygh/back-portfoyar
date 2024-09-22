from django.db import models
from core.models import TimeStampMixin


class OptionStrategy(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name="نام استراتژی", max_length=255)

    key = models.CharField(verbose_name="نام کلید", max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "استراتژی"
        verbose_name_plural = "۰۰) استراتژی‌ها"


class RiskLevel(TimeStampMixin, models.Model):
    option_strategy = models.ForeignKey(
        OptionStrategy,
        on_delete=models.CASCADE,
        related_name="risk_level",
        blank=True,
        null=True,
    )

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

    LEVEL_CHOICES = [
        ("no_risk", "استراتژی‌های بدون ریسک"),
        ("low_risk", "استراتژی‌های با ریسک کم"),
        ("high_risk", "استراتژی‌های با ریسک زیاد"),
        ("lower_risk", "استراتژی‌های کاهنده ریسک"),
        ("higher_risk_roi", "استراتژی‌های افزایش ریسک و بازدهی"),
    ]

    level = models.CharField(
        verbose_name=("سطح ریسک"),
        choices=LEVEL_CHOICES,
        max_length=255,
        default="no_risk",
    )

    name = models.CharField(verbose_name=("نام"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "سطح ریسک"
        verbose_name_plural = "۰۰) سطوح ریسک"

    def save(self, *args, **kwargs):
        if self.level == self.LEVEL_CHOICES[0][0]:
            self.name = self.LEVEL_CHOICES[0][1]

        elif self.level == self.LEVEL_CHOICES[1][0]:
            self.name = self.LEVEL_CHOICES[1][1]

        elif self.level == self.LEVEL_CHOICES[2][0]:
            self.name = self.LEVEL_CHOICES[2][1]

        elif self.level == self.LEVEL_CHOICES[3][0]:
            self.name = self.LEVEL_CHOICES[3][1]

        elif self.level == self.LEVEL_CHOICES[4][0]:
            self.name = self.LEVEL_CHOICES[4][1]

        else:
            self.name = "نامشخص"

        if self.profit_status == "limited_profit":
            self.name = self.name + " | " + "با سود محدود"
        else:
            self.name = self.name + " | " + "با سود نامحدود"

        super().save(*args, **kwargs)
