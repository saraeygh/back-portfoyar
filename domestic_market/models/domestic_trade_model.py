from core.models import TimeStampMixin
from django.db import models

from . import DomesticCommodity, DomesticProducer


class DomesticTrade(TimeStampMixin, models.Model):
    commodity = models.ForeignKey(
        DomesticCommodity, verbose_name=("کالا"), on_delete=models.CASCADE
    )

    producer = models.ForeignKey(
        DomesticProducer,
        verbose_name=("تولید کننده"),
        on_delete=models.CASCADE,
    )

    commodity_name = models.CharField(verbose_name="نام کالا", max_length=255)

    symbol = models.CharField(verbose_name="نماد", max_length=255)

    contract_type = models.CharField(
        max_length=200,
        verbose_name="نوع قرارداد",
    )

    trade_date = models.DateField(
        ("تاریخ میلادی معامله"),
        auto_now=False,
        auto_now_add=False,
    )

    trade_date_shamsi = models.CharField(("تاریخ شمسی معامله"), max_length=255)

    delivery_date = models.DateField(
        ("تاریخ تحویل"),
        auto_now=False,
        auto_now_add=False,
    )

    delivery_date_shamsi = models.CharField(("تاریخ شمسی تحویل"), max_length=255)

    base_price = models.BigIntegerField(
        verbose_name="قیمت پایه عرضه",
    )

    min_price = models.BigIntegerField(
        verbose_name="حداقل قیمت",
        blank=True,
        null=True,
    )

    close_price = models.BigIntegerField(verbose_name="قیمت میانگین پایانی")

    max_price = models.BigIntegerField(
        verbose_name="حداکثر قیمت",
        blank=True,
        null=True,
    )

    value = models.BigIntegerField(verbose_name="ارزش معامله (هزار ریال)")

    currency = models.CharField(
        max_length=255, verbose_name="ارز", default="ریال", blank=True, null=True
    )

    unit = models.CharField(max_length=255, verbose_name="واحد")

    competition = models.DecimalField(
        verbose_name="درصد رقابت", max_digits=20, decimal_places=2
    )

    supply_volume = models.DecimalField(
        verbose_name="حجم عرضه", max_digits=20, decimal_places=2
    )

    demand_volume = models.DecimalField(
        verbose_name="حجم تقاضا", max_digits=20, decimal_places=2
    )

    contract_volume = models.DecimalField(
        verbose_name="حجم قرارداد", max_digits=20, decimal_places=2
    )

    broker = models.CharField(max_length=255, verbose_name="کارگزار")

    supply_pk = models.CharField(max_length=64, verbose_name="کد عرضه", default="-")

    def __str__(self):
        return f"{self.commodity_name}: {self.trade_date_shamsi}"

    class Meta:
        verbose_name = "معامله"
        verbose_name_plural = "۰۵) معاملات"
