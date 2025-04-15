from django.contrib import admin
from fund.models import FundInfo


@admin.register(FundInfo)
class FundInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fund_type",
        "reg_no",
        "name",
        "initiation_date",
        "last_date",
        "ins_code",
    )
    list_display_links = ("id",)
    ordering = ("-created_at",)

    search_fields = (
        "reg_no",
        "name",
        "fund_manager",
        "ins_code",
    )

    list_filter = (
        "fund_type",
        "invest_type",
        "dividend_interval_period",
        "guaranteed_earning_rate",
    )
