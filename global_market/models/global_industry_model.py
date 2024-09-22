from core.models import TimeStampMixin
from django.db import models


class GlobalIndustry(TimeStampMixin, models.Model):
    name = models.CharField(verbose_name=("نام صنعت"), max_length=255)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "صنعت"
        verbose_name_plural = "۱) صنایع"
