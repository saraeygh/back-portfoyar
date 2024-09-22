from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models

from domestic_market.models import DomesticProducer


class DomesticFavoriteProducerReport(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_producer_report",
    )

    producer = models.ForeignKey(
        verbose_name="تولید کننده",
        to=DomesticProducer,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_producer_report",
    )

    class Meta:
        verbose_name = "Domestic: تولید کننده مورد علاقه برای گزارش"
        verbose_name_plural = "Domestic: تولید کننده مورد علاقه برای گزارش"
        unique_together = (
            "user",
            "producer",
        )
