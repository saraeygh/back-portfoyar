from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from django.db import models

from core.models import TimeStampMixin
from account.models import Feature

# PRE-DEFINED TRANSACTION DESCRIPTION
RECEIPT_CREATED = "receipt-created"

# METHOD CHOICES
ZARINPAL = "zarinpal"
DEFAULT_METHOD = ZARINPAL
METHOD_CHOICES = [
    (ZARINPAL, "زرین‌پال"),
]


class Receipt(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        to=User,
        verbose_name="کاربر",
        on_delete=models.PROTECT,
        related_name="receipts",
    )

    feature = models.ForeignKey(
        to=Feature,
        verbose_name="طرح",
        on_delete=models.PROTECT,
        related_name="receipts",
    )

    discount_type = models.ForeignKey(
        to=ContentType,
        verbose_name="تخفیف",
        on_delete=models.PROTECT,
        related_name="receipts",
        blank=True,
        null=True,
    )
    discount_id = models.PositiveIntegerField(
        verbose_name="آیدی تخفیف", blank=True, null=True
    )
    discount_object = GenericForeignKey("discount_type", "discount_id")

    receipt_id = models.CharField(verbose_name="شناسه تراکنش", max_length=64)

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
        verbose_name="توضیحات", max_length=128, default=RECEIPT_CREATED
    )

    class Meta:
        verbose_name = "رسید تراکنش‌"
        verbose_name_plural = "۱) رسید تراکنش‌ها"


class Transaction(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        to=User,
        verbose_name="کاربر",
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    tx_id = models.CharField(verbose_name="شناسه تراکنش", max_length=64)

    plan = models.JSONField(verbose_name="طرح", default=dict)

    discount = models.JSONField(verbose_name="تخفیف", default=dict)

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
        verbose_name="توضیحات", max_length=128, default=RECEIPT_CREATED
    )

    class Meta:
        verbose_name = "تراکنش‌"
        verbose_name_plural = "۲) تراکنش‌ها"
