from django.db import models

from core.models import TimeStampMixin

from . import FundType

UNKNOWN = "نامشخص"


class FundInfo(TimeStampMixin, models.Model):

    fund_type = models.ForeignKey(
        to=FundType, on_delete=models.PROTECT, related_name="funds"
    )

    reg_no = models.CharField(verbose_name="شماره ثبت", max_length=16)

    name = models.CharField(verbose_name="نام", max_length=128)

    invest_type = models.CharField(
        verbose_name="نوع سرمایه‌گذاری", max_length=32, default=UNKNOWN
    )

    initiation_date = models.DateField(verbose_name="شروع")

    dividend_interval_period = models.IntegerField(
        verbose_name="دوره تقسیم سود", default=0
    )

    guaranteed_earning_rate = models.IntegerField(
        verbose_name="بازدهی تضمین شده", default=0
    )

    last_date = models.DateField(verbose_name="آخرین به‌روزرسانی")

    fund_manager = models.CharField(
        verbose_name="مدیر سرمایه‌گذاری", max_length=128, default=UNKNOWN
    )

    # market_maker = models.CharField(
    #     verbose_name="بازارساز", max_length=128, default=UNKNOWN
    # )

    website = models.CharField(verbose_name="وبسایت", max_length=64, default=UNKNOWN)

    guarantor = models.CharField(
        verbose_name="تضمین کننده", max_length=128, default=UNKNOWN
    )

    # investment_manager = models.CharField(
    #     verbose_name="مدیران سرمایه‌گذاری", max_length=128, default=UNKNOWN
    # )

    # national_id = models.CharField(
    #     verbose_name="شناسه ملی", max_length=64, default=UNKNOWN
    # )

    ins_code = models.CharField(
        verbose_name="شناسه بورسی", max_length=64, default=UNKNOWN
    )

    def __str__(self) -> str:
        return str(f"{self.name} ({self.reg_no})")

    class Meta:
        verbose_name = "اطلاعات کلی صندوق"
        verbose_name_plural = "۲) اطلاعات کلی صندوق‌ها"
