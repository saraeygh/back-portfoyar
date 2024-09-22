from core.models import TimeStampMixin
from django.db import models

from . import DomesticProducer, DomesticCommodity


class DomesticMonthlySell(TimeStampMixin, models.Model):
    producer = models.ForeignKey(
        DomesticProducer,
        verbose_name=("تولید کننده"),
        on_delete=models.CASCADE,
    )

    commodity = models.ForeignKey(
        DomesticCommodity, verbose_name=("کالا"), on_delete=models.CASCADE
    )

    commodity_name = models.CharField(verbose_name="نام کالا", max_length=255)

    symbol = models.CharField(verbose_name="نماد", max_length=255)

    start_date = models.DateField(
        ("تاریخ میلادی ابتدای ماه"),
        auto_now=False,
        auto_now_add=False,
    )

    end_date = models.DateField(
        ("تاریخ میلادی آخر ماه"),
        auto_now=False,
        auto_now_add=False,
    )

    unit = models.CharField(max_length=255, verbose_name="واحد")

    min_value = models.BigIntegerField(verbose_name="حداقل ارزش ماهانه")
    max_value = models.BigIntegerField(verbose_name="حداکثر ارزش ماهانه")
    mean_value = models.BigIntegerField(verbose_name="میانگین ارزش ماهانه")
    total_value = models.BigIntegerField(verbose_name="کل ارزش ماهانه")

    monthly_min_base_price = models.BigIntegerField(
        verbose_name="کمترین قیمت پایه عرضه ماه",
    )
    monthly_max_base_price = models.BigIntegerField(
        verbose_name="بیشترین قیمت پایه عرضه ماه",
    )
    monthly_mean_base_price = models.BigIntegerField(
        verbose_name="میانگین قیمت پایه عرضه ماه",
    )

    monthly_min_price = models.BigIntegerField(
        verbose_name="حداقل قیمت ماه",
        blank=True,
        null=True,
    )
    monthly_max_price = models.BigIntegerField(
        verbose_name="حداکثر قیمت ماه",
        blank=True,
        null=True,
    )
    monthly_mean_price = models.BigIntegerField(
        verbose_name="میانگین قیمت ماه",
        blank=True,
        null=True,
    )

    monthly_min_close_price = models.BigIntegerField(
        verbose_name="کمترین قیمت میانگین پایانی ماه"
    )
    monthly_max_close_price = models.BigIntegerField(
        verbose_name="بیشترین قیمت میانگین پایانی ماه"
    )
    monthly_mean_close_price = models.BigIntegerField(
        verbose_name="میانگین قیمت میانگین پایانی ماه"
    )

    def __str__(self):
        return str(f"{self.producer} - {self.commodity_name}")

    class Meta:
        verbose_name = "فروش ماهانه"
        verbose_name_plural = "۰۶) فروش ماهانه"
        unique_together = [
            "producer",
            "commodity",
            "commodity_name",
            "start_date",
            "end_date",
        ]
