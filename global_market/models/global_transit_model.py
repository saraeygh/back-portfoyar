from core.models import TimeStampMixin
from django.db import models


class GlobalTransit(TimeStampMixin, models.Model):
    transit_type = models.CharField(
        verbose_name=("نوع ترانزیت"),
        max_length=255,
    )

    transit_unit = models.CharField(verbose_name=("واحد"), max_length=255)

    def __str__(self):
        return str(self.transit_type)

    class Meta:
        verbose_name = "ترانزیت"
        verbose_name_plural = "۴) ترانزیت‌ها"
