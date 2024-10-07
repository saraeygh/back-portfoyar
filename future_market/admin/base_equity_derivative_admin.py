from django.contrib import admin
from future_market.models import BaseEquity, Derivative


@admin.register(BaseEquity)
class BaseEquityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "base_equity_key",
        "base_equity_name",
        "base_equity_col",
        "base_equity_value",
    )
    list_display_links = ("base_equity_name",)
    ordering = ("-updated_at",)

    search_fields = ("base_equity_key", "base_equity_name", "base_equity_col")

    list_filter = ("base_equity_key", "base_equity_col")


@admin.register(Derivative)
class DerivativeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("base_equity",)
    list_display = (
        "id",
        "derivative_key",
        "derivative_name",
        "derivative_col",
        "derivative_value",
    )
    list_display_links = ("derivative_name",)
    ordering = ("-updated_at",)

    search_fields = ("derivative_key", "derivative_name", "derivative_value")

    list_filter = ("derivative_key", "derivative_col")
