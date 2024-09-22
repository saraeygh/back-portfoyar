from core.models import TimeStampMixin
from django.db import models

from . import DomesticIndustry


class DomesticCommodityType(TimeStampMixin, models.Model):
    industry = models.ForeignKey(
        DomesticIndustry,
        verbose_name=("صنعت"),
        on_delete=models.CASCADE,
        related_name="commodity_types",
    )

    name = models.CharField(verbose_name=("نوع کالا"), max_length=255)
    code = models.IntegerField(verbose_name=("کد نوع کالا"))

    def __str__(self):
        return f"{self.name} - {self.industry.name}"

    class Meta:
        verbose_name = "نوع کالا"
        verbose_name_plural = "۰۲) انواع کالا"
