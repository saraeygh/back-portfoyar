from core.models import TimeStampMixin
from django.db import models

from . import DomesticCommodityType


class DomesticCommodity(TimeStampMixin, models.Model):
    commodity_type = models.ForeignKey(
        DomesticCommodityType,
        verbose_name=("نوع کالا"),
        on_delete=models.CASCADE,
        related_name="commodities",
    )

    name = models.CharField(verbose_name=("نام کالا"), max_length=255)
    code = models.IntegerField(verbose_name=("کد کالا"))

    def __str__(self):
        return f"{self.name} - {self.commodity_type.name} - {self.commodity_type.industry.name}"

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "۰۳) کالاها"
