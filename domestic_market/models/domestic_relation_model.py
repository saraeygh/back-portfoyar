from core.models import TimeStampMixin
from django.db import models
from stock_market.models import StockInstrument
from . import DomesticProducer


class DomesticRelation(TimeStampMixin, models.Model):
    domestic_producer = models.ForeignKey(
        to=DomesticProducer,
        on_delete=models.CASCADE,
        verbose_name=("تولید کننده بورس کالا"),
        related_name="relations",
    )

    stock_instrument = models.ForeignKey(
        to=StockInstrument,
        on_delete=models.CASCADE,
        verbose_name=("سهم"),
        related_name="domestic_relations",
    )

    class Meta:
        verbose_name = "ارتباط"
        verbose_name_plural = "۰۹) ارتباط‌ها"
        unique_together = ["domestic_producer", "stock_instrument"]
