from core.models import TimeStampMixin
from django.db import models
from . import StockInstrument


class StockRawHistory(TimeStampMixin, models.Model):
    instrument = models.ForeignKey(
        to=StockInstrument,
        on_delete=models.CASCADE,
        related_name="price_history",
        verbose_name="نماد",
    )

    trade_date = models.DateField(verbose_name="تاریخ")

    trade_count = models.IntegerField(verbose_name="تعداد معاملات")

    volume = models.BigIntegerField(verbose_name="حجم معاملات")

    value = models.BigIntegerField(verbose_name="ارزش معاملات")

    yesterday_price = models.IntegerField(verbose_name="قیمت دیروز")

    open = models.IntegerField(verbose_name="اولین قیمت")

    close = models.IntegerField(verbose_name="آخرین قیمت")

    low = models.IntegerField(verbose_name="کمترین قیمت")

    high = models.IntegerField(verbose_name="بیشترین قیمت")

    close_mean = models.IntegerField(verbose_name="قیمت پایانی")

    individual_buy_count = models.IntegerField(verbose_name="تعداد خرید حقیقی")
    individual_buy_volume = models.BigIntegerField(verbose_name="حجم خرید حقیقی")
    individual_buy_value = models.BigIntegerField(verbose_name="ارزش خرید حقیقی")

    legal_buy_count = models.IntegerField(verbose_name="تعداد خرید حقوقی")
    legal_buy_volume = models.BigIntegerField(verbose_name="حجم خرید حقوقی")
    legal_buy_value = models.BigIntegerField(verbose_name="ارزش خرید حقوقی")

    individual_sell_count = models.IntegerField(verbose_name="تعداد فروش حقیقی")
    individual_sell_volume = models.BigIntegerField(verbose_name="حجم فروش حقیقی")
    individual_sell_value = models.BigIntegerField(verbose_name="ارزش فروش حقیقی")

    legal_sell_count = models.IntegerField(verbose_name="تعداد فروش حقوقی")
    legal_sell_volume = models.BigIntegerField(verbose_name="حجم فروش حقوقی")
    legal_sell_value = models.BigIntegerField(verbose_name="ارزش فروش حقوقی")

    def __str__(self):
        return f"{self.instrument.symbol} ({self.trade_date})"

    class Meta:
        verbose_name = "تاریخچه قیمت (تعدیل نشده)"
        verbose_name_plural = "۱۳) تاریخچه‌ قمیت‌ها (تعدیل نشده)"
        unique_together = ["instrument", "trade_date"]
