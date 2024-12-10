from django.contrib.auth.models import User
from django.db import models

from core.models import TimeStampMixin

# PRE-DEFINED TRANSACTION DESCRIPTION
TX_CREATED = "TX Created"

# METHOD CHOICES
ZARINPAL = "zarinpal"
DEFAULT_METHOD = ZARINPAL
METHOD_CHOICES = [
    (ZARINPAL, "زرین‌پال"),
]


class Transaction(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        to=User,
        verbose_name="کاربر",
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    tx_id = models.CharField(verbose_name="شناسه تراکنش", max_length=64)

    plan = models.CharField(
        verbose_name="طرح",
        max_length=255,
        default="feat: ..., dur: ..., login: ..., pr: ..., dis_per: ..., dis_pr: ...",
    )

    discount = models.CharField(
        verbose_name="تخفیف",
        max_length=255,
        default="tp: ..., name: ..., dis_per: ..., code: ... | ..., st: ..., ex: ..., use: ... | ... | ...",
    )

    price = models.IntegerField(verbose_name="قیمت")

    method = models.CharField(
        verbose_name="روش پرداخت",
        max_length=16,
        choices=METHOD_CHOICES,
        default=DEFAULT_METHOD,
    )

    pay_id = models.CharField(verbose_name="شناسه پرداخت", max_length=128, default="")

    is_confirmed = models.BooleanField(verbose_name="تایید شده؟", default=False)

    tracking_id = models.CharField(verbose_name="کد رهگیری", max_length=128, default="")

    description = models.CharField(
        verbose_name="توضیحات", max_length=128, default=TX_CREATED
    )

    class Meta:
        verbose_name = "تراکنش‌"
        verbose_name_plural = "۱) تراکنش‌ها"
