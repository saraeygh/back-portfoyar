from core.models import TimeStampMixin
from django.db import models

from . import GlobalIndustry


class GlobalCommodityType(TimeStampMixin, models.Model):
    industry = models.ForeignKey(
        GlobalIndustry,
        verbose_name=("صنعت"),
        on_delete=models.CASCADE,
        related_name="commodity_types",
    )

    name = models.CharField(verbose_name=("نوع کالا"), max_length=255)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "نوع کالا"
        verbose_name_plural = "۲) انواع کالا"
