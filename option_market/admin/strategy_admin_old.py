from django.contrib import admin
from option_market.models import Strategy


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "collection_key")

    list_display_links = ("id", "name")

    ordering = ("name",)

    search_fields = ("name", "collection_key")

    fieldsets = (("استراتژی", {"fields": ("name", "collection_key")}),)
