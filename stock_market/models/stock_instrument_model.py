from core.models import TimeStampMixin
from django.db import models
from . import StockIndustrialGroup


class StockInstrument(TimeStampMixin, models.Model):
    industrial_group = models.ForeignKey(
        to=StockIndustrialGroup, on_delete=models.CASCADE, related_name="instruments"
    )

    MARKET_TYPE_CHOICES = [(1, "بورس"), (2, "فرابورس")]
    market_type = models.IntegerField(
        verbose_name="نوع بازار", choices=MARKET_TYPE_CHOICES
    )

    PAPER_TYPE_CHOICES = [
        (1, "سهام"),
        (2, "بازار پایه فرابورس"),
        (3, "تسهیلات مسکن"),
        (4, "حق تقدم"),
        (5, "اوراق بدهی"),
        (6, "اختیار معامله"),
        (7, "آتی"),
        (8, "صندوق‌های سرمایه‌گذاری"),
        (9, "بورس کالا"),
    ]
    paper_type = models.IntegerField(
        verbose_name="نوع اوراق", choices=PAPER_TYPE_CHOICES
    )

    ins_code = models.CharField(verbose_name=("کد نماد"), max_length=255, unique=True)

    ins_id = models.CharField(verbose_name=("شناسه نماد"), max_length=255, unique=True)

    symbol = models.CharField(verbose_name=("نماد"), max_length=255)

    name = models.CharField(verbose_name=("نام"), max_length=255)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = "نماد"
        verbose_name_plural = "۱۲) نمادها"
        constraints = [
            models.UniqueConstraint(fields=["id"], name="stock_instrument_unique_id")
        ]
