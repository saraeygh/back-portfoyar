from core.models import TimeStampMixin
from django.db import models


class DomesticIndustry(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name=("نام صنعت"), max_length=255)
    code = models.IntegerField(verbose_name=("کد صنعت"))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "صنعت"
        verbose_name_plural = "۰۱) صنایع"
