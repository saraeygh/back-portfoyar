from django.contrib import admin
from option_market.models import OptionValue


@admin.register(OptionValue)
class OptionValueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "date_shamsi",
        "call_value",
        "put_value",
        "option_value",
        "put_to_call",
        "option_to_market",
    )

    list_display_links = ("id", "date_shamsi")

    ordering = ("-date",)

    search_fields = ("date_shamsi",)

    readonly_fields = (
        "date",
        "call_value",
        "put_value",
        "option_value",
        "put_to_call",
        "option_to_market",
    )
