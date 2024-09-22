from core.models import TimeStampMixin
from django.db import models

from . import GlobalCommodity, GlobalTransit


class GlobalTrade(TimeStampMixin, models.Model):
    commodity = models.ForeignKey(
        GlobalCommodity, verbose_name=("کالا"), on_delete=models.CASCADE
    )

    transit = models.ForeignKey(
        GlobalTransit,
        verbose_name=("ترانزیت"),
        on_delete=models.CASCADE,
    )

    trade_date = models.DateField(
        ("تاریخ معامله"),
        auto_now=False,
        auto_now_add=False,
    )

    price = models.DecimalField(("قیمت"), max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.transit)

    class Meta:
        verbose_name = "معامله"
        verbose_name_plural = "۵) معاملات"
