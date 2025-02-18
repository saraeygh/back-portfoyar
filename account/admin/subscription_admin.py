from django.contrib import admin
from django.contrib.messages import success
from account.models import (
    Subscription,
    DisabledSubscription,
    UserDiscount,
    DisabledUserDiscount,
)


class MyPropertyFilter(admin.SimpleListFilter):
    title = "وضعیت فعال بودن"
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        return (("True", "فعال"), ("False", "غیرفعال"))

    def queryset(self, request, queryset):
        subscription_ids = list()
        query_param = self.value()
        if query_param is None:
            return queryset

        for subscription in queryset:
            if eval(query_param) and subscription.is_active:
                subscription_ids.append(subscription.id)
            if not eval(query_param) and not subscription.is_active:
                subscription_ids.append(subscription.id)

        queryset = Subscription.objects.filter(id__in=subscription_ids)
        return queryset


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=True)

    autocomplete_fields = ("user", "feature")
    list_display = (
        "id",
        "is_enabled",
        "user",
        "full_name",
        "feature",
        "is_active",
        "remained_days",
        "start_at_shamsi",
        "end_at_shamsi",
        "desc",
    )
    list_display_links = ("user", "feature")
    ordering = ("-updated_at",)

    search_fields = ("id", "user__username", "feature__name", "is_enabled")

    list_filter = ("feature__name", MyPropertyFilter)

    def delete_queryset(self, request, queryset):
        for feature_discount in queryset:
            feature_discount.is_enabled = False
            feature_discount.save()

        success(request, "تخفیف‌های انتخاب شده با موفقیت غیرفعال شدند")


@admin.register(DisabledSubscription)
class DisabledSubscriptionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=False)

    autocomplete_fields = ("user", "feature")
    list_display = (
        "id",
        "is_enabled",
        "user",
        "full_name",
        "feature",
        "is_active",
        "remained_days",
        "start_at_shamsi",
        "end_at_shamsi",
        "desc",
    )
    list_display_links = ("user", "feature")
    ordering = ("-updated_at",)

    search_fields = ("id", "user__username", "feature__name", "is_enabled")

    list_filter = ("feature__name", MyPropertyFilter)

    def delete_queryset(self, request, queryset):
        for feature_discount in queryset:
            feature_discount.is_enabled = False
            feature_discount.save()

        success(request, "تخفیف‌های انتخاب شده با موفقیت غیرفعال شدند")


@admin.register(UserDiscount)
class UserDiscountAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=True)

    autocomplete_fields = ("user", "feature")
    list_display = (
        "id",
        "user",
        "full_name",
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


@admin.register(DisabledUserDiscount)
class DisabledUserDiscountAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_enabled=False)

    autocomplete_fields = ("user", "feature")
    list_display = (
        "id",
        "user",
        "full_name",
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
