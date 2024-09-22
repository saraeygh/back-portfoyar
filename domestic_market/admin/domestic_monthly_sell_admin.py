from django.contrib import admin
from domestic_market.models import DomesticMonthlySell
from persiantools.jdatetime import JalaliDate


@admin.register(DomesticMonthlySell)
class DomesticMonthlySellAdmin(admin.ModelAdmin):
    autocomplete_fields = ("producer", "commodity")
    list_display = (
        "id",
        "producer",
        "commodity_name",
        "commodity",
        "start_date_shamsi",
        "end_date_shamsi",
        "total_value",
        "monthly_mean_base_price",
        "monthly_mean_price",
        "monthly_mean_close_price",
    )

    list_display_links = (
        "producer",
        "commodity_name",
        "commodity",
        "start_date_shamsi",
        "end_date_shamsi",
        "total_value",
        "monthly_mean_base_price",
        "monthly_mean_price",
        "monthly_mean_close_price",
    )

    ordering = ("-end_date",)

    search_fields = ("producer__name", "commodity_name", "commodity__name")

    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "اطلاعات کلی",
            {"fields": ("producer", "commodity", "commodity_name", "symbol")},
        ),
        (
            "اطلاعات تاریخ",
            {
                "fields": (
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            "ارزش معاملات",
            {"fields": ("min_value", "max_value", "mean_value", "total_value")},
        ),
        (
            "اطلاعات قیمت عرضه",
            {
                "fields": (
                    "monthly_min_base_price",
                    "monthly_max_base_price",
                    "monthly_mean_base_price",
                )
            },
        ),
        (
            "اطلاعات قیمت فروش",
            {
                "fields": (
                    "monthly_min_price",
                    "monthly_max_price",
                    "monthly_mean_price",
                )
            },
        ),
        (
            "اطلاعات میانگین قیمت پایانی",
            {
                "fields": (
                    "monthly_min_close_price",
                    "monthly_max_close_price",
                    "monthly_mean_close_price",
                )
            },
        ),
        (
            "سایر اطلاعات",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="شروع ماه")
    def start_date_shamsi(self, obj: DomesticMonthlySell):
        shamsi = (JalaliDate(obj.start_date)).strftime("%Y-%m-%d")

        return shamsi

    @admin.display(description="پایان ماه")
    def end_date_shamsi(self, obj: DomesticMonthlySell):
        shamsi = (JalaliDate(obj.end_date)).strftime("%Y-%m-%d")

        return shamsi
