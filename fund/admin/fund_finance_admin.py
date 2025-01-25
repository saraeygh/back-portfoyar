from django.contrib import admin
from fund.models import FundFinance


@admin.register(FundFinance)
class FundFinanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fund_info",
        "cancel_nav",
        "issue_nav",
        "statistical_nav",
        "fund_size",
        "net_asset",
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "six_month",
        "annual",
    )

    list_display_links = ("fund_info",)
    ordering = ("-created_at",)

    search_fields = ("fund_info__fund_type__name", "fund_info__fund_type__code")
