from core.models import TimeStampMixin
from django.db import models
from . import StockIndustrialGroup

BOURSE_TYPE = 1
FARABOURSE_TYPE = 2
MARKET_TYPE_CHOICES = [(BOURSE_TYPE, "بورس"), (FARABOURSE_TYPE, "فرابورس")]


STOCK = 1
BASE_MARKET = 2
ACCOMMODATION = 3
STOCK_PRIORITY = 4
DEBT_PAPER = 5
OPTION = 6
FUTURES = 7
FUND = 8
COMMODITY_MARKET = 9
PAPER_TYPE_CHOICES = [
    (STOCK, "سهام"),
    (BASE_MARKET, "بازار پایه فرابورس"),
    (ACCOMMODATION, "تسهیلات مسکن"),
    (STOCK_PRIORITY, "حق تقدم"),
    (DEBT_PAPER, "اوراق بدهی"),
    (OPTION, "اختیار معامله"),
    (FUTURES, "آتی"),
    (FUND, "صندوق‌های سرمایه‌گذاری"),
    (COMMODITY_MARKET, "بورس کالا"),
]


class StockInstrument(TimeStampMixin, models.Model):
    industrial_group = models.ForeignKey(
        to=StockIndustrialGroup, on_delete=models.CASCADE, related_name="instruments"
    )

    market_type = models.IntegerField(
        verbose_name="نوع بازار", choices=MARKET_TYPE_CHOICES
    )

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
