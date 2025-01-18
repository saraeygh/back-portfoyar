from django.db import models

from core.models import TimeStampMixin

# BASE EQUITY KEYS
SANDOQ_MARKET = "updateSandoqMarketsInfo"
GAVAHI_MARKET = "updateGavahiMarketsInfo"
CDC_MARKET = "updateCDCMarketsInfo"

# DERIVATIVE KEYS
FUTURE_MARKET = "updateFutureMarketsInfo"
OPTION_MARKET = "updateMarketsInfo"

# BASE EQUITY & DERIVATIVE UNIQUE COLUMNS
ID = "ID"
CONTRACT_CODE = "ContractCode"
CALL_CONTRACT_ID = "CallContractID"
PUT_CONTRACT_ID = "PutContractID"

BASE_EQUITY_KEY_CHOICES = [
    (SANDOQ_MARKET, "صندوق‌های کالایی (updateSandoqMarketsInfo)"),
    (
        GAVAHI_MARKET,
        "گواهی سپرده کالایی - غیر شمش و سکه طلا (updateGavahiMarketsInfo)",
    ),
    (CDC_MARKET, "شمش و سکه طلا (updateCDCMarketsInfo)"),
]


class FutureBaseEquity(TimeStampMixin, models.Model):

    base_equity_key = models.CharField(
        verbose_name="دسته‌بندی", max_length=100, choices=BASE_EQUITY_KEY_CHOICES
    )

    base_equity_name = models.CharField(verbose_name="نام دارایی پایه", max_length=255)

    derivative_symbol = models.CharField(
        verbose_name="نماد قرارداد مشتقه", max_length=100
    )

    unique_identifier = models.CharField(
        verbose_name="شناسه", max_length=100, blank=True, null=True
    )

    def __str__(self) -> str:
        return str(self.base_equity_name)

    class Meta:
        verbose_name = "دارایی پایه آتی"
        verbose_name_plural = "۱) (آتی) دارایی‌های پایه"


class OptionBaseEquity(TimeStampMixin, models.Model):

    base_equity_key = models.CharField(
        verbose_name="دسته‌بندی", max_length=64, choices=BASE_EQUITY_KEY_CHOICES
    )

    base_equity_name = models.CharField(verbose_name="نام دارایی پایه", max_length=128)

    derivative_symbol = models.CharField(
        verbose_name="نماد قرارداد مشتقه", max_length=32
    )

    unique_identifier = models.CharField(
        verbose_name="شناسه", max_length=128, blank=True, null=True
    )

    def __str__(self) -> str:
        return str(self.base_equity_name)

    class Meta:
        verbose_name = "دارایی پایه آپشن"
        verbose_name_plural = "۱) (آپشن) دارایی‌های پایه"
