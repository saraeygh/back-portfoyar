from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models

from domestic_market.models import DomesticProducer, DomesticCommodity, DomesticTrade


class DomesticFavoritePriceChartByProducer(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_price_chart_by_producer",
    )

    producer = models.ForeignKey(
        verbose_name="تولید کننده",
        to=DomesticProducer,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_price_chart_by_producer",
    )

    commodity = models.ForeignKey(
        verbose_name="کالا",
        to=DomesticCommodity,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_price_chart_by_producer",
    )

    trade_commodity_name = models.ForeignKey(
        verbose_name="نام کالا",
        to=DomesticTrade,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_price_chart_by_producer",
    )

    class Meta:
        verbose_name = "Domestic: نمودار قیمت مورد علاقه بر اساس تولید کننده"
        verbose_name_plural = "Domestic: نمودارهای قیمت مورد علاقه بر اساس تولید کننده"
        unique_together = ("user", "producer", "commodity", "trade_commodity_name")
