from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models

from global_market.models import (
    GlobalCommodity,
    GlobalCommodityType,
    GlobalIndustry,
    GlobalTransit,
)


class GlobalFavoritePriceChart(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="global_favorite_price_chart",
    )

    industry = models.ForeignKey(
        verbose_name="صنعت",
        to=GlobalIndustry,
        on_delete=models.CASCADE,
        related_name="global_favorite_price_chart",
    )

    commodity_type = models.ForeignKey(
        verbose_name="نوع کالا",
        to=GlobalCommodityType,
        on_delete=models.CASCADE,
        related_name="global_favorite_price_chart",
    )

    commodity = models.ForeignKey(
        verbose_name="کالا",
        to=GlobalCommodity,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="global_favorite_price_chart",
    )

    transit = models.ForeignKey(
        verbose_name="ترانزیت",
        to=GlobalTransit,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="global_favorite_price_chart",
    )

    class Meta:
        verbose_name = "Global: نمودار قیمت مورد علاقه"
        verbose_name_plural = "Global: نمودارهای قیمت مورد علاقه"
        unique_together = (
            "user",
            "industry",
            "commodity_type",
            "commodity",
            "transit",
        )
