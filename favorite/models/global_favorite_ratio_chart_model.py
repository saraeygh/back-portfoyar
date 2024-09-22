from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models

from global_market.models import (
    GlobalCommodity,
    GlobalCommodityType,
    GlobalIndustry,
    GlobalTransit,
)


class GlobalFavoriteRatioChart(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="global_favorite_ratio_chart",
    )

    industry_1 = models.ForeignKey(
        verbose_name="صنعت ۱",
        to=GlobalIndustry,
        on_delete=models.CASCADE,
        related_name="global_favorite_ratio_chart_industry_1",
    )

    commodity_type_1 = models.ForeignKey(
        verbose_name="نوع کالا ۱",
        to=GlobalCommodityType,
        on_delete=models.CASCADE,
        related_name="global_favorite_ratio_chart_commodity_type_1",
    )

    commodity_1 = models.ForeignKey(
        verbose_name="کالا ۱",
        to=GlobalCommodity,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="global_favorite_ratio_chart_commodity_1",
    )

    transit_1 = models.ForeignKey(
        verbose_name="ترانزیت ۱",
        to=GlobalTransit,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="global_favorite_ratio_chart_transit_1",
    )

    industry_2 = models.ForeignKey(
        verbose_name="صنعت ۲",
        to=GlobalIndustry,
        on_delete=models.CASCADE,
        related_name="global_favorite_ratio_chart_industry_2",
    )

    commodity_type_2 = models.ForeignKey(
        verbose_name="نوع کالا ۲",
        to=GlobalCommodityType,
        on_delete=models.CASCADE,
        related_name="global_favorite_ratio_chart_commodity_type_2",
    )

    commodity_2 = models.ForeignKey(
        verbose_name="کالا ۲",
        to=GlobalCommodity,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="global_favorite_ratio_chart_commodity_2",
    )

    transit_2 = models.ForeignKey(
        verbose_name="ترانزیت ۲",
        to=GlobalTransit,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="global_favorite_ratio_chart_transit_2",
    )

    class Meta:
        verbose_name = "Global: نسبت قیمت مورد علاقه"
        verbose_name_plural = "Global: نسبت‌های قیمت مورد علاقه"
        unique_together = (
            "user",
            "industry_1",
            "commodity_type_1",
            "commodity_1",
            "transit_1",
            "industry_2",
            "commodity_type_2",
            "commodity_2",
            "transit_2",
        )
