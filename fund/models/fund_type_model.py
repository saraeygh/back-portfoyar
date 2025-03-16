from django.db import models

from core.models import TimeStampMixin

FIXED_INCOME_FUND = 4
MIXED_FUND = 7


class FundType(TimeStampMixin, models.Model):

    code = models.IntegerField(verbose_name="کد")

    name = models.CharField(verbose_name="دسته‌بندی", max_length=64)

    is_active = models.BooleanField(verbose_name="فعال", default=True)

    def __str__(self) -> str:
        return str(f"{self.name} [{self.code}]")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "۱) دسته‌بندی‌ها"
