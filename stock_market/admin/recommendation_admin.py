import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from stock_market.models import RecommendationConfig
from stock_market.models.recommendation_config_model import (
    MoneyFlow,
    BuyPressure,
    BuyValue,
    BuyRatio,
    SellRatio,
    ROI,
    ValueChange,
    CallValueChange,
    PutValueChange,
    OptionPriceSpread,
    GlobalPositiveRange,
    GlobalNegativeRange,
    DomesticPositiveRange,
    DomesticNegativeRange,
)


class MoneyFlowInline(admin.StackedInline):
    model = MoneyFlow
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class BuyPressureInline(admin.StackedInline):
    model = BuyPressure
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class BuyValueInline(admin.StackedInline):
    model = BuyValue
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class BuyRatioInline(admin.StackedInline):
    model = BuyRatio
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class SellRatioInline(admin.StackedInline):
    model = SellRatio
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class ROIInline(admin.StackedInline):
    model = ROI
    fields = ("is_enabled", "ascending", "weight", "threshold_value", "duration")


class ValueChangeInline(admin.StackedInline):
    model = ValueChange
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class CallValueChangeInline(admin.StackedInline):
    model = CallValueChange
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class PutValueChangeInline(admin.StackedInline):
    model = PutValueChange
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class OptionPriceSpreadInline(admin.StackedInline):
    model = OptionPriceSpread
    fields = ("is_enabled", "ascending", "weight", "threshold_value")


class GlobalPositiveRangeInline(admin.StackedInline):
    model = GlobalPositiveRange
    fields = ("is_enabled", "ascending", "weight", "threshold_value", "duration")


class GlobalNegativeRangeInline(admin.StackedInline):
    model = GlobalNegativeRange
    fields = ("is_enabled", "ascending", "weight", "threshold_value", "duration")


class DomesticPositiveRangeInline(admin.StackedInline):
    model = DomesticPositiveRange
    fields = (
        "is_enabled",
        "ascending",
        "weight",
        "threshold_value",
        "duration",
        "min_commodity_ratio",
    )


class DomesticNegativeRangeInline(admin.StackedInline):
    model = DomesticNegativeRange
    fields = (
        "is_enabled",
        "ascending",
        "weight",
        "threshold_value",
        "duration",
        "min_commodity_ratio",
    )


@admin.register(RecommendationConfig)
class RecommendationConfigAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = (
        "id",
        "is_default",
        "user",
        "name",
        "money_flow_weight",
        "buy_pressure_weight",
        "buy_value_weight",
        "buy_ratio_weight",
        "sell_ratio_weight",
        "roi_weight",
        "value_change_weight",
        "call_value_change_weight",
        "put_value_change_weight",
        "option_price_spread_weight",
        "global_positive_range_weight",
        "global_negative_range_weight",
        "domestic_positive_range_weight",
        "domestic_negative_range_weight",
        "created_at_shamsi",
        "updated_at_shamsi",
    )
    list_display_links = ("id", "user")
    ordering = ("-updated_at",)

    search_fields = ("id", "name", "user__username")

    inlines = (
        MoneyFlowInline,
        BuyPressureInline,
        BuyValueInline,
        BuyRatioInline,
        SellRatioInline,
        ROIInline,
        ValueChangeInline,
        CallValueChangeInline,
        PutValueChangeInline,
        OptionPriceSpreadInline,
        GlobalPositiveRangeInline,
        GlobalNegativeRangeInline,
        DomesticPositiveRangeInline,
        DomesticNegativeRangeInline,
    )

    ############################################################### MONEY FLOW
    @admin.display(description="ورود پول")
    def money_flow_weight(self, obj: RecommendationConfig):
        is_enabled = obj.money_flow.is_enabled
        return obj.money_flow.weight if is_enabled else "غیرفعال"

    ############################################################# BUY PRESSURE
    @admin.display(description="قدرت خرید")
    def buy_pressure_weight(self, obj: RecommendationConfig):
        is_enabled = obj.buy_pressure.is_enabled
        return obj.buy_pressure.weight if is_enabled else "غیرفعال"

    ################################################################ BUY VALUE
    @admin.display(description="خرید درشت")
    def buy_value_weight(self, obj: RecommendationConfig):
        is_enabled = obj.buy_value.is_enabled
        return obj.buy_value.weight if is_enabled else "غیرفعال"

    ################################################################ BUY RATIO
    @admin.display(description="نسبت خرید")
    def buy_ratio_weight(self, obj: RecommendationConfig):
        is_enabled = obj.buy_ratio.is_enabled
        return obj.buy_ratio.weight if is_enabled else "غیرفعال"

    ############################################################### SELL RATIO
    @admin.display(description="نسبت فروش")
    def sell_ratio_weight(self, obj: RecommendationConfig):
        is_enabled = obj.sell_ratio.is_enabled
        return obj.sell_ratio.weight if is_enabled else "غیرفعال"

    ###################################################################### ROI
    @admin.display(description="بازدهی")
    def roi_weight(self, obj: RecommendationConfig):
        is_enabled = obj.roi.is_enabled
        return obj.roi.weight if is_enabled else "غیرفعال"

    ############################################################# VALUE CHANGE
    @admin.display(description="ارزش معاملات")
    def value_change_weight(self, obj: RecommendationConfig):
        is_enabled = obj.value_change.is_enabled
        return obj.value_change.weight if is_enabled else "غیرفعال"

    ######################################################## CALL VALUE CHANGE
    @admin.display(description="ارزش اختیار خرید")
    def call_value_change_weight(self, obj: RecommendationConfig):
        is_enabled = obj.call_value_change.is_enabled
        return obj.call_value_change.weight if is_enabled else "غیرفعال"

    ######################################################### PUT VALUE CHANGE
    @admin.display(description="ارزش اختیار فروش")
    def put_value_change_weight(self, obj: RecommendationConfig):
        is_enabled = obj.put_value_change.is_enabled
        return obj.put_value_change.weight if is_enabled else "غیرفعال"

    ###################################################### OPTION PRICE SPREAD
    @admin.display(description="اسپرد قیمتی اختیار")
    def option_price_spread_weight(self, obj: RecommendationConfig):
        is_enabled = obj.option_price_spread.is_enabled
        return obj.option_price_spread.weight if is_enabled else "غیرفعال"

    #################################################### GLOBAL POSITIVE RANGE
    @admin.display(description="بیشترین رشد جهانی")
    def global_positive_range_weight(self, obj: RecommendationConfig):
        is_enabled = obj.global_positive_range.is_enabled
        return obj.global_positive_range.weight if is_enabled else "غیرفعال"

    #################################################### GLOBAL NEGATIVE RANGE
    @admin.display(description="بیشترین افت جهانی")
    def global_negative_range_weight(self, obj: RecommendationConfig):
        is_enabled = obj.global_negative_range.is_enabled
        return obj.global_negative_range.weight if is_enabled else "غیرفعال"

    ################################################## DOMESTIC POSITIVE RANGE
    @admin.display(description="بیشترین رشد داخلی")
    def domestic_positive_range_weight(self, obj: RecommendationConfig):
        is_enabled = obj.domestic_positive_range.is_enabled
        return obj.domestic_positive_range.weight if is_enabled else "غیرفعال"

    ################################################## DOMESTIC NEGATIVE RANGE
    @admin.display(description="بیشترین افت داخلی")
    def domestic_negative_range_weight(self, obj: RecommendationConfig):
        is_enabled = obj.domestic_negative_range.is_enabled
        return obj.domestic_negative_range.weight if is_enabled else "غیرفعال"

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: RecommendationConfig):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: RecommendationConfig):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
