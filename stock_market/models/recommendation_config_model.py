from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampMixin

RELATED_NAMES = [
    "money_flow",
    "buy_pressure",
    "buy_value",
    "buy_ratio",
    "sell_ratio",
    "roi",
    "value_change",
    "call_value_change",
    "put_value_change",
    "option_price_spread",
    "global_positive_range",
    "global_negative_range",
    "domestic_positive_range",
    "domestic_negative_range",
]

FUNDAMENTAL_CATEGORY = "foundamental"
MARKETWATCH_CATEGORY = "marketwatch"
CATEGORY_CHOICES = [
    (FUNDAMENTAL_CATEGORY, "بنیادی"),
    (MARKETWATCH_CATEGORY, "تابلوخوانی"),
]


class RecommendationConfig(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        verbose_name="کاربر",
        to=User,
        on_delete=models.CASCADE,
        related_name="configs",
    )

    name = models.CharField(
        verbose_name="نام تنظیمات پیشنهاد سهم",
        max_length=255,
        blank=True,
        null=True,
    )

    is_default = models.BooleanField(verbose_name="پیش‌فرض", default=False)

    class Meta:
        verbose_name = "تنظیمات پیشنهاد سهم"
        verbose_name_plural = "۳۱) تنظیمات پیشنهاد سهم"

    def get_related_objects_as_dict(self):
        related_objects = {}
        for attr in RELATED_NAMES:
            try:
                related_objects[attr] = getattr(self, attr)
            except AttributeError:
                continue
        return related_objects


class MoneyFlow(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="money_flow",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=-100_000)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class BuyPressure(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="buy_pressure",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class BuyValue(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="buy_value",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class BuyRatio(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="buy_ratio",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class SellRatio(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="sell_ratio",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=False)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


WEEKLY = 7
MONTHLY = 30
QUARTERLY = 90
HALF_YEARLY = 180
YEARLY = 365
THREE_YEARLY = 1095
ROI_DURATIONS_CHOICES = [
    (WEEKLY, "هفتگی"),
    (MONTHLY, "ماهانه"),
    (QUARTERLY, "سه‌ ماهه"),
    (HALF_YEARLY, "شش‌ ماهه"),
    (YEARLY, "یک‌ ساله"),
    (THREE_YEARLY, "سه‌ ساله"),
]


class ROI(TimeStampMixin, models.Model):

    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="roi",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=False)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=-100_000)
    duration = models.IntegerField(
        verbose_name="دوره عملکرد", choices=ROI_DURATIONS_CHOICES, default=90
    )
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class ValueChange(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="value_change",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=-100_000)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class CallValueChange(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="call_value_change",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=-100_000)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class PutValueChange(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="put_value_change",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=False)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=-100_000)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


class OptionPriceSpread(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="option_price_spread",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=6)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=-100_000)
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="marketwatch"
    )


COMMODITY_MARKETS_DURATIONS_CHOICES = [
    (WEEKLY, "هفتگی"),
    (MONTHLY, "ماهانه"),
    (QUARTERLY, "سه‌ ماهه"),
    (HALF_YEARLY, "شش‌ ماهه"),
    (YEARLY, "یک‌ ساله"),
]


class GlobalPositiveRange(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="global_positive_range",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=10)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    duration = models.IntegerField(
        verbose_name="دوره عملکرد",
        choices=COMMODITY_MARKETS_DURATIONS_CHOICES,
        default=30,
    )
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="foundamental"
    )


class GlobalNegativeRange(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="global_negative_range",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=False)
    weight = models.IntegerField(verbose_name="وزن", default=10)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    duration = models.IntegerField(
        verbose_name="دوره عملکرد",
        choices=COMMODITY_MARKETS_DURATIONS_CHOICES,
        default=30,
    )
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="foundamental"
    )


class DomesticPositiveRange(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="domestic_positive_range",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=True)
    weight = models.IntegerField(verbose_name="وزن", default=10)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    duration = models.IntegerField(
        verbose_name="دوره عملکرد",
        choices=COMMODITY_MARKETS_DURATIONS_CHOICES,
        default=30,
    )
    min_commodity_ratio = models.IntegerField(
        verbose_name="حداقل مقدار نسبت محصول", default=0
    )
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="foundamental"
    )


class DomesticNegativeRange(TimeStampMixin, models.Model):
    recommendation = models.OneToOneField(
        verbose_name="کانفیگ",
        to=RecommendationConfig,
        on_delete=models.CASCADE,
        related_name="domestic_negative_range",
    )

    is_enabled = models.BooleanField(verbose_name="فعال", default=False)
    ascending = models.BooleanField(verbose_name="رابطه مستقیم", default=False)
    weight = models.IntegerField(verbose_name="وزن", default=10)
    threshold_value = models.IntegerField(verbose_name="مقدار آستانه", default=0)
    duration = models.IntegerField(
        verbose_name="دوره عمکلرد",
        choices=COMMODITY_MARKETS_DURATIONS_CHOICES,
        default=30,
    )
    min_commodity_ratio = models.IntegerField(
        verbose_name="حداقل مقدار نسبت محصول", default=0
    )
    category = models.CharField(
        verbose_name=("نوع"), choices=CATEGORY_CHOICES, default="foundamental"
    )
