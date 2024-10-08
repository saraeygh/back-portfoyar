from core.models import TimeStampMixin
from django.db import models

# BASE EQUITY KEYS
FUND_INFO = "updateSandoqMarketsInfo"
COMMODITY_INFO = "updateGavahiMarketsInfo"
GOLD_INFO = "updateCDCMarketsInfo"

# DERIVATIVE KEYS
FUTURE_INFO = "updateFutureMarketsInfo"
OPTION_INFO = "updateMarketsInfo"

# BASE EQUITY & DERIVATIVE UNIQUE COLUMNS
ID = "ID"
CONTRACT_CODE = "ContractCode"
CALL_CONTRACT_ID = "CallContractID"
PUT_CONTRACT_ID = "PutContractID"

BASE_EQUITY_KEY_CHOICES = [
    (FUND_INFO, "صندوق‌های کالایی (updateSandoqMarketsInfo)"),
    (
        COMMODITY_INFO,
        "گواهی سپرده کالایی - غیر شمش و سکه طلا (updateGavahiMarketsInfo)",
    ),
    (GOLD_INFO, "شمش و سکه طلا (updateCDCMarketsInfo)"),
]


class BaseEquity(TimeStampMixin, models.Model):

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
        verbose_name = "دارایی پایه"
        verbose_name_plural = "۱) دارایی‌های پایه"
