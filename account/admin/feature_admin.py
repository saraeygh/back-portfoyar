from django.contrib import admin
from account.models import Feature, FeatureDiscount


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_enabled",
        "name",
        "duration",
        "price",
        "has_discount",
        "discount_percent",
        "discounted_price",
        "login_count",
    )
    list_display_links = ("name",)
    ordering = ("-updated_at",)

    search_fields = ("id", "name", "price")

    list_filter = ("name", "duration", "has_discount", "login_count", "is_enabled")

    search_fields = ("id", "name")


@admin.register(FeatureDiscount)
class FeatureDiscountAdmin(admin.ModelAdmin):
    autocomplete_fields = ("feature",)
    list_display = (
        "id",
        "feature",
        "name",
        "is_enabled",
        "discount_percent",
        "has_discount_code",
        "discount_code",
        "has_start",
        "start_at_shamsi",
        "has_expiry",
        "expire_at_shamsi",
        "has_max_use_count",
        "used_count",
        "max_use_count",
    )
    list_display_links = ("name",)
    ordering = ("-updated_at",)

    search_fields = ("id", "name", "discount_code")

    list_filter = (
        "is_enabled",
        "has_discount_code",
        "has_start",
        "has_expiry",
        "has_max_use_count",
    )
