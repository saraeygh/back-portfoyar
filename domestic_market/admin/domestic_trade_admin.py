from django.contrib import admin
from core.utils import get_deviation_percent
from domestic_market.models import DomesticTrade


@admin.register(DomesticTrade)
class DomesticTradeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("commodity", "producer")
    list_display = (
        "id",
        "symbol",
        "producer",
        "commodity",
        "commodity_name",
        "contract_type",
        "trade_date_shamsi",
        "delivery_date_shamsi",
        "base_price",
        "close_price",
        "value",
        "competition",
        "contract_volume",
        "supply_volume",
        "demand_volume",
    )

    list_display_links = (
        "commodity",
        "producer",
        "contract_type",
        "trade_date_shamsi",
        "delivery_date_shamsi",
        "base_price",
        "close_price",
        "value",
        "competition",
    )

    list_filter = ("contract_type",)

    ordering = ("-trade_date",)

    search_fields = (
        "symbol",
        "contract_type",
        "trade_date_shamsi",
        "delivery_date_shamsi",
        "commodity__name",
        "commodity__commodity_type__name",
        "commodity__commodity_type__industry__name",
        "producer__name",
    )

    fieldsets = (
        (
            "اطلاعات کلی",
            {"fields": ("commodity", "producer", "contract_type")},
        ),
        (
            "اطلاعات مالی",
            {
                "fields": (
                    "value",
                    "close_price",
                    "base_price",
                    "min_price",
                    "max_price",
                    "currency",
                    "competition",
                    "supply_volume",
                    "demand_volume",
                    "contract_volume",
                )
            },
        ),
        (
            "تاریخ‌ها",
            {"fields": ("trade_date", "delivery_date")},
        ),
        (
            "سایر اطلاعات",
            {
                "fields": (
                    "commodity_name",
                    "symbol",
                    "unit",
                    "trade_date_shamsi",
                    "delivery_date_shamsi",
                    "broker",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if obj.base_price == 0:
            obj.competition = 0
        else:
            obj.competition = get_deviation_percent(obj.close_price, obj.base_price)

        return super().save_model(request, obj, form, change)
