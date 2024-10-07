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

DERIVATIVE_KEY_CHOICES = [
    (FUTURE_INFO, "آتی (updateFutureMarketsInfo)"),
    (OPTION_INFO, "اختیار معامله (updateMarketsInfo)"),
]

BASE_EQUITY_COL_CHOICES = [
    (ID, "ID"),
    (CONTRACT_CODE, "ContractCode"),
]

DERIVATIVE_COL_CHOICES = [
    (CONTRACT_CODE, "ContractCode"),
    (CALL_CONTRACT_ID, "CallContractID"),
    (PUT_CONTRACT_ID, "PutContractID"),
]


class BaseEquity(TimeStampMixin, models.Model):

    base_equity_key = models.CharField(
        verbose_name="دسته‌بندی", max_length=100, choices=BASE_EQUITY_KEY_CHOICES
    )
    base_equity_col = models.CharField(
        verbose_name="نام ستون یکتا",
        max_length=100,
        choices=BASE_EQUITY_COL_CHOICES,
    )
    base_equity_value = models.CharField(verbose_name="مقدار ستون یکتا", max_length=100)
    base_equity_name = models.CharField(verbose_name="نام دارایی پایه", max_length=255)

    class Meta:
        verbose_name = "دارایی پایه"
        verbose_name_plural = "۱) دارایی‌های پایه"


class Derivative(TimeStampMixin, models.Model):

    base_equity = models.ForeignKey(
        to=BaseEquity,
        verbose_name="دارایی پایه",
        on_delete=models.CASCADE,
        related_name="derivatives",
    )

    derivative_key = models.CharField(
        verbose_name="قرارداد مشتقه", max_length=100, choices=DERIVATIVE_KEY_CHOICES
    )
    derivative_col = models.CharField(
        verbose_name="نام ستون یکتای قرارداد مشتقه",
        max_length=100,
        choices=DERIVATIVE_COL_CHOICES,
    )
    derivative_value = models.CharField(verbose_name="مقدار ستون یکتا", max_length=100)
    derivative_name = models.CharField(verbose_name="نام قرارداد", max_length=255)

    class Meta:
        verbose_name = "قرارداد مشتقه"
        verbose_name_plural = "۲) قراردادهای مشتقه"
