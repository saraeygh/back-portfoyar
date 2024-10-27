from django.contrib import admin
from account.models import Feature


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "duration",
        "price",
        "has_discount",
        "discount_percent",
        "discounted_price",
    )
    list_display_links = ("name",)
    ordering = ("-updated_at",)

    search_fields = ("id", "name", "price")

    list_filter = ("name", "duration", "has_discount")

    search_fields = ("id", "name")
