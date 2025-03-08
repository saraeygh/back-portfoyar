from core.models import TimeStampMixin
from django.db import models


class StockIndustrialGroup(TimeStampMixin, models.Model):
    code = models.IntegerField(verbose_name=("کد صنعت"), unique=True)
    name = models.CharField(verbose_name=("نام صنعت"), max_length=255)
    priority = models.IntegerField(verbose_name=("اولویت"), default=99)

    def __str__(self):
        return f"{self.code}: ({self.name})"

    class Meta:
        verbose_name = "صنعت"
        verbose_name_plural = "۱۱) صنایع"
