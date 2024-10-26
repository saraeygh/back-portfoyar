from django.contrib import admin
from account.models import Subscription


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
    autocomplete_fields = ("user",)
    list_display = (
        "id",
        "user",
        "feature",
        "is_active",
        "remained_days",
        "start_at_shamsi",
        "end_at_shamsi",
    )
    list_display_links = ("user", "feature")
    ordering = ("-updated_at",)

    search_fields = ("id", "user__username", "feature")

    list_filter = ("feature", MyPropertyFilter)
