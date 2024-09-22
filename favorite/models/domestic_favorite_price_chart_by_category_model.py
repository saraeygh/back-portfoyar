from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models

from domestic_market.models import (
    DomesticCommodity,
    DomesticCommodityType,
    DomesticIndustry,
    DomesticProducer,
    DomesticTrade,
)


class DomesticFavoritePriceChartByCategory(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_price_chart_by_category",
    )

    industry = models.ForeignKey(
        verbose_name="صنعت",
        to=DomesticIndustry,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_price_chart_by_category",
    )

    commodity_type = models.ForeignKey(
        verbose_name="نوع کالا",
        to=DomesticCommodityType,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_price_chart_by_category",
    )

    commodity = models.ForeignKey(
        verbose_name="کالا",
        to=DomesticCommodity,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_price_chart_by_category",
    )

    producer = models.ForeignKey(
        verbose_name="تولید کننده",
        to=DomesticProducer,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_price_chart_by_category",
    )

    trade_commodity_name = models.ForeignKey(
        verbose_name="نام کالا",
        to=DomesticTrade,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_price_chart_by_category",
    )

    class Meta:
        verbose_name = "Domestic: نمودار قیمت مورد علاقه بر اساس دسته‌بندی"
        verbose_name_plural = "Domestic: نمودارهای قیمت مورد علاقه بر اساس دسته‌بندی"
        unique_together = (
            "user",
            "industry",
            "commodity_type",
            "commodity",
            "producer",
            "trade_commodity_name",
        )
