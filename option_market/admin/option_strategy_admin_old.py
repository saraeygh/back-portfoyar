from django.contrib import admin
from option_market.models import OptionStrategy, RiskLevel


@admin.register(OptionStrategy)
class OptionStrategyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "key")

    list_display_links = ("id", "name")

    ordering = ("name",)

    search_fields = ("name", "key")

    fieldsets = (("استراتژی", {"fields": ("name", "key")}),)


@admin.register(RiskLevel)
class RiskLevelyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "profit_status", "level", "option_strategy")

    list_display_links = ("id", "name", "profit_status", "level", "option_strategy")

    ordering = ("-updated_at",)

    search_fields = ("name", "profit_status", "level", "option_strategy__name")

    fieldsets = (
        ("استراتژی", {"fields": ("name", "profit_status", "level", "option_strategy")}),
    )

    list_filter = ("name", "profit_status", "level")
