from django.contrib import admin
from future_market.models import FutureBaseEquity, OptionBaseEquity


@admin.register(FutureBaseEquity)
class FutureBaseEquityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "base_equity_key",
        "base_equity_name",
        "derivative_symbol",
        "unique_identifier",
    )
    list_display_links = ("base_equity_name",)
    ordering = ("-updated_at",)

    search_fields = (
        "base_equity_key",
        "base_equity_name",
        "derivative_symbol",
        "unique_identifier",
    )

    list_filter = ("derivative_symbol",)


@admin.register(OptionBaseEquity)
class OptionBaseEquityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "base_equity_key",
        "base_equity_name",
        "derivative_symbol",
        "unique_identifier",
    )
    list_display_links = ("base_equity_name",)
    ordering = ("-updated_at",)

    search_fields = (
        "base_equity_key",
        "base_equity_name",
        "derivative_symbol",
        "unique_identifier",
    )

    list_filter = ("derivative_symbol",)
