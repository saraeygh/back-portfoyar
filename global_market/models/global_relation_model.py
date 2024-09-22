from core.models import TimeStampMixin
from django.db import models
from .global_commodity_type_model import GlobalCommodityType
from stock_market.models import StockInstrument


class GlobalRelation(TimeStampMixin, models.Model):
    global_commodity_type = models.ForeignKey(
        to=GlobalCommodityType,
        on_delete=models.CASCADE,
        verbose_name=("نوع کالا"),
        related_name="relations",
    )

    stock_instrument = models.ForeignKey(
        to=StockInstrument,
        on_delete=models.CASCADE,
        verbose_name=("سهم"),
        related_name="global_relations",
    )

    class Meta:
        verbose_name = "ارتباط"
        verbose_name_plural = "۶) ارتباط‌ها"
        unique_together = ["global_commodity_type", "stock_instrument"]
