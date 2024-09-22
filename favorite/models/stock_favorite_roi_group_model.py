from core.models import TimeStampMixin
from django.contrib.auth.models import User
from django.db import models

from stock_market.models import StockInstrument


class StockFavoriteROIGroup(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="favorite_roi_groups",
    )

    name = models.CharField(verbose_name="نام", max_length=255)

    class Meta:
        verbose_name = "Stock: گروه سهم‌های مورد علاقه"
        verbose_name_plural = "Stock: گروه‌ سهم‌های مورد علاقه"


class ROIGroupInstrument(TimeStampMixin, models.Model):
    group = models.ForeignKey(
        verbose_name="گروه",
        to=StockFavoriteROIGroup,
        on_delete=models.CASCADE,
        related_name="instruments",
    )

    instrument = models.ForeignKey(
        verbose_name="نماد",
        to=StockInstrument,
        on_delete=models.CASCADE,
        related_name="groups",
    )

    class Meta:
        unique_together = ["group", "instrument"]
