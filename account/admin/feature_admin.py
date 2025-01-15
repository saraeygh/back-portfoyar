from django.contrib import admin
from django.contrib.messages import success
from account.models import (
    Feature,
    DisabledFeature,
    FeatureDiscount,
    DisabledFeatureDiscount,
)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=True)

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


@admin.register(DisabledFeature)
class DisabledFeatureAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=False)

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
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=True)

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

    def delete_queryset(self, request, queryset):
        for feature_discount in queryset:
            feature_discount.is_enabled = False
            feature_discount.save()

        success(request, "تخفیف‌های انتخاب شده با موفقیت غیرفعال شدند")


@admin.register(DisabledFeatureDiscount)
class DisabledFeatureDiscountAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=False)

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

    def delete_queryset(self, request, queryset):
        for feature_discount in queryset:
            feature_discount.is_enabled = False
            feature_discount.save()

        success(request, "تخفیف‌های انتخاب شده با موفقیت غیرفعال شدند")
