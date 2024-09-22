from core.models import TimeStampMixin
from django.db import models

from . import GlobalCommodityType


class GlobalCommodity(TimeStampMixin, models.Model):
    commodity_type = models.ForeignKey(
        GlobalCommodityType,
        verbose_name=("نوع کالا"),
        on_delete=models.CASCADE,
        related_name="commodities",
    )

    name = models.CharField(verbose_name=("نام کالا"), max_length=255)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "۳) کالاها"
