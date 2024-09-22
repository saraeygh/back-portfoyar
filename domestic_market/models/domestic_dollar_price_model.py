from core.models import TimeStampMixin
from django.db import models


class DomesticDollarPrice(TimeStampMixin, models.Model):
    class Meta:
        verbose_name = "قیمت دلار"
        verbose_name_plural = "۰۷) قیمت‌های دلار"

    date = models.DateField(verbose_name="تاریخ میلادی", unique=True)
    date_shamsi = models.CharField(verbose_name="تاریخ شمسی", unique=True)

    nima = models.IntegerField(verbose_name="نرخ نیمایی")
    azad = models.IntegerField(verbose_name="نرخ آزاد")

    def __str__(self):
        return str(
            f"آزاد: {self.azad}"
            + " | "
            + f"نیما: {self.nima}"
            + " | "
            + f"تاریخ: {str(self.date_shamsi)}"
        )
