from core.models import TimeStampMixin
from django.db import models


class DomesticProducer(TimeStampMixin, models.Model):
    name = models.CharField(
        verbose_name=("تولید کننده"),
        max_length=255,
    )

    code = models.IntegerField(verbose_name=("کد تولید کننده"))

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "تولید کننده"
        verbose_name_plural = "۰۴) تولید کننده‌ها"
        constraints = [models.UniqueConstraint(fields=["id"], name="unique_id")]
