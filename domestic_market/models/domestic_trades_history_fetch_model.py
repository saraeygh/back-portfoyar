from core.models import TimeStampMixin
from django.db import models


class DomesticTradesHistoryFetch(TimeStampMixin, models.Model):
    class Meta:
        verbose_name = "تاریخچه دریافت اطلاعات بورس کالا"
        verbose_name_plural = "۱۰) تاریخچه دریافت اطلاعات بورس کالا"

    start_date = models.CharField(verbose_name="از تاریخ")
    end_date = models.CharField(verbose_name="تا تاریخ")

    request_sent = models.BooleanField(verbose_name="ارسال درخواست")
    received_trades = models.BooleanField(
        verbose_name="دریافت اطلاعات",
        default=False,
    )
    number_of_trades_received = models.IntegerField(
        verbose_name="رکوردهای دریافت شده", default=0
    )

    start_populating_db = models.BooleanField(
        verbose_name="شروع ثبت در دیتابیس", default=False
    )
    db_populated = models.BooleanField(
        verbose_name="اتمام ثبت در دیتابیس", default=False
    )
    number_of_populated_trades = models.IntegerField(
        verbose_name="رکوردهای ثبت شده", default=0
    )
