from django.db import models

from core.models import TimeStampMixin

from . import FundInfo


class FundFinance(TimeStampMixin, models.Model):

    fund_info = models.ForeignKey(
        to=FundInfo, on_delete=models.PROTECT, related_name="funds"
    )

    cancel_nav = models.IntegerField(verbose_name="ابطال")

    issue_nav = models.IntegerField(verbose_name="صدور")

    statistical_nav = models.IntegerField(verbose_name="آماری")

    fund_size = models.BigIntegerField(verbose_name="اندازه")

    net_asset = models.BigIntegerField(verbose_name="اندازه")

    daily = models.DecimalField(
        verbose_name="روزانه", max_digits=5, decimal_places=2, default=0
    )

    weekly = models.DecimalField(
        verbose_name="هفتگی", max_digits=5, decimal_places=2, default=0
    )

    monthly = models.DecimalField(
        verbose_name="ماهانه", max_digits=5, decimal_places=2, default=0
    )

    quarterly = models.DecimalField(
        verbose_name="سه ماهه", max_digits=5, decimal_places=2, default=0
    )

    six_month = models.DecimalField(
        verbose_name="شش ماهه", max_digits=5, decimal_places=2, default=0
    )

    annual = models.DecimalField(
        verbose_name="سالانه", max_digits=5, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = "اطلاعات مالی صندوق‌"
        verbose_name_plural = "۳) اطلاعات مالی صندوق‌ها"
