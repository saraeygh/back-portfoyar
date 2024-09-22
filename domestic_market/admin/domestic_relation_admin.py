from django.contrib import admin

from domestic_market.models import DomesticRelation


@admin.register(DomesticRelation)
class DomesticRelationAdmin(admin.ModelAdmin):
    autocomplete_fields = ("domestic_producer", "stock_instrument")
    list_display = ("id", "domestic_producer", "stock_instrument")

    list_display_links = ("id", "domestic_producer", "stock_instrument")

    ordering = ("-updated_at",)

    search_fields = (
        "domestic_producer__name",
        "stock_instrument__name",
        "stock_instrument__symbol",
    )
