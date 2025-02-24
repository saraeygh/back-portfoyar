from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from django.db import models

from core.models import TimeStampMixin
from account.models import Feature, SUBSCRIPTION_FEATURE_CHOICES


# PRE-DEFINED TRANSACTION DESCRIPTION
RECEIPT_CREATED = "receipt-created"

# METHOD CHOICES
ZARINPAL = "zarinpal"
DEFAULT_METHOD = ZARINPAL
METHOD_CHOICES = [
    (ZARINPAL, "زرین‌پال"),
]

FEATURES = {feature[0]: feature[1] for feature in SUBSCRIPTION_FEATURE_CHOICES}
METHODS = {method[0]: method[1] for method in METHOD_CHOICES}


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
        verbose_name="روش پرداخت", max_length=16, choices=METHOD_CHOICES, default=""
    )

    pay_id = models.CharField(verbose_name="شناسه پرداخت", max_length=128, default="")

    is_confirmed = models.BooleanField(verbose_name="تایید شده؟", default=False)

    tracking_id = models.CharField(verbose_name="کد رهگیری", max_length=128, default="")

    description = models.CharField(
        verbose_name="توضیحات", max_length=128, default=RECEIPT_CREATED
    )

    @property
    def feature_name(self):
        return FEATURES.get(self.feature.name, "")

    @property
    def feature_duration(self):
        return self.feature.duration

    @property
    def feature_login_count(self):
        return self.feature.login_count

    @property
    def feature_price(self):
        return self.feature.price

    @property
    def feature_discount(self):
        if self.feature.has_discount:
            return self.feature.discount_percent
        return 0

    @property
    def discount_name(self):
        if self.discount_type:
            return self.discount_object.name
        return ""

    @property
    def discount_percent(self):
        if self.discount_type:
            return self.discount_object.discount_percent
        return 0

    @property
    def method_name(self):
        return METHODS.get(self.method, "")

    class Meta:
        verbose_name = "رسید تراکنش‌"
        verbose_name_plural = "۱) رسید تراکنش‌ها"
