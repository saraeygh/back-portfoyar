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


class DomesticFavoriteRatioChartByCategory(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_category",
    )

    industry_1 = models.ForeignKey(
        verbose_name="صنعت ۱",
        to=DomesticIndustry,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_category_industry_1",
    )

    commodity_type_1 = models.ForeignKey(
        verbose_name="نوع کالا ۱",
        to=DomesticCommodityType,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_category_commodity_type_1",
    )

    commodity_1 = models.ForeignKey(
        verbose_name="کالا ۱",
        to=DomesticCommodity,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_category_commodity_1",
    )

    producer_1 = models.ForeignKey(
        verbose_name="تولید کننده ۱",
        to=DomesticProducer,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_category_transit_1",
    )

    trade_commodity_name_1 = models.ForeignKey(
        verbose_name="۱ نام کالا",
        to=DomesticTrade,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_category_trade_commodity_name_1",
    )

    industry_2 = models.ForeignKey(
        verbose_name="صنعت ۲",
        to=DomesticIndustry,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_category_industry_2",
    )

    commodity_type_2 = models.ForeignKey(
        verbose_name="نوع کالا ۲",
        to=DomesticCommodityType,
        on_delete=models.CASCADE,
        related_name="domestic_favorite_ratio_chart_by_category_commodity_type_2",
    )

    commodity_2 = models.ForeignKey(
        verbose_name="کالا ۲",
        to=DomesticCommodity,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_category_commodity_2",
    )

    producer_2 = models.ForeignKey(
        verbose_name="تولید کننده ۲",
        to=DomesticProducer,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_category_transit_2",
    )

    trade_commodity_name_2 = models.ForeignKey(
        verbose_name="۲ نام کالا",
        to=DomesticTrade,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domestic_favorite_ratio_chart_by_category_trade_commodity_name_2",
    )

    class Meta:
        verbose_name = "Domestic: نسبت قیمت مورد علاقه بر اساس دسته‌بندی"
        verbose_name_plural = "Domestic: نسبت‌های قیمت مورد علاقه بر اساس دسته‌بندی"
        unique_together = (
            "user",
            "industry_1",
            "commodity_type_1",
            "commodity_1",
            "producer_1",
            "trade_commodity_name_1",
            "industry_2",
            "commodity_type_2",
            "commodity_2",
            "producer_2",
            "trade_commodity_name_2",
        )
