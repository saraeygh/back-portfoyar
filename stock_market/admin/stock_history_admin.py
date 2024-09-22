from django.contrib import admin
from stock_market.models import StockRawHistory
from persiantools.jdatetime import JalaliDate


@admin.register(StockRawHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    autocomplete_fields = ("instrument",)

    list_display = (
        "id",
        "instrument",
        "trade_date_shamsi",
        "trade_count",
        "volume",
        "value",
        "yesterday_price",
        "open",
        "close",
        "low",
        "high",
        "close_mean",
        "individual_buy_count",
        "individual_buy_volume",
        "individual_buy_value",
        "legal_buy_count",
        "legal_buy_volume",
        "legal_buy_value",
        "individual_sell_count",
        "individual_sell_volume",
        "individual_sell_value",
        "legal_sell_count",
        "legal_sell_volume",
        "legal_sell_value",
    )

    list_display_links = ("id", "instrument")

    ordering = ("-updated_at",)

    search_fields = ("instrument__name", "instrument__symbol")

    @admin.display(description="تاریخ شمسی")
    def trade_date_shamsi(self, obj: StockRawHistory):
        shamsi = (JalaliDate(obj.trade_date)).strftime("%Y-%m-%d")

        return shamsi
