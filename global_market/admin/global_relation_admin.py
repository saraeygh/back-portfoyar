from django.contrib import admin
from global_market.models import GlobalRelation


@admin.register(GlobalRelation)
class GlobalRelationAdmin(admin.ModelAdmin):
    autocomplete_fields = ("global_commodity_type", "stock_instrument")
    list_display = ("id", "global_commodity_type", "stock_instrument")

    list_display_links = ("id", "global_commodity_type", "stock_instrument")

    ordering = ("-updated_at",)

    search_fields = (
        "global_commodity_type__name",
        "stock_instrument__name",
        "stock_instrument__symbol",
    )
