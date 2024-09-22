from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models

from domestic_market.models import DomesticProducer, DomesticCommodity, DomesticTrade


class DomesticFavoriteRatioChartByProducer(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_producer",
    )

    producer_1 = models.ForeignKey(
        verbose_name="تولید کننده ۱",
        to=DomesticProducer,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_producer_1",
    )

    commodity_1 = models.ForeignKey(
        verbose_name="کالا ۱",
        to=DomesticCommodity,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_producer_commodity_1",
    )

    trade_commodity_name_1 = models.ForeignKey(
        verbose_name="۱ نام کالا",
        to=DomesticTrade,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_producer_commodity_name_1",
    )

    producer_2 = models.ForeignKey(
        verbose_name="تولید کننده ۲",
        to=DomesticProducer,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_producer_2",
    )

    commodity_2 = models.ForeignKey(
        verbose_name="کالا ۲",
        to=DomesticCommodity,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_producer_commodity_2",
    )

    trade_commodity_name_2 = models.ForeignKey(
        verbose_name="۲ نام کالا",
        to=DomesticTrade,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_producer_commodity_name_2",
    )

    class Meta:
        verbose_name = "Domestic: نسبت قیمت مورد علاقه بر اساس تولید کننده"
        verbose_name_plural = "Domestic: نسبت‌های قیمت مورد علاقه بر اساس تولید کننده"
        unique_together = (
            "user",
            "producer_1",
            "commodity_1",
            "trade_commodity_name_1",
            "producer_2",
            "commodity_2",
            "trade_commodity_name_2",
        )
