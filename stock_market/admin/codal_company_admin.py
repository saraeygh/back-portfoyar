import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from stock_market.models import CodalCompany


@admin.register(CodalCompany)
class CodalCompanyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "symbol",
        "name",
        "codal_id",
        "publisher_state",
        "codal_t",
        "codal_IG",
        "codal_RT",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = ("id", "symbol", "name", "codal_id")

    list_filter = ("publisher_state", "codal_t", "codal_IG", "codal_RT")

    ordering = ("-updated_at",)

    search_fields = (
        "id",
        "symbol",
        "name",
        "codal_id",
        "codal_t",
        "codal_IG",
        "codal_RT",
    )

    fieldsets = (
        (
            "اطلاعات کلی",
            {"fields": ("symbol", "name")},
        ),
        (
            "سایر اطلاعات",
            {
                "fields": (
                    "codal_id",
                    "codal_t",
                    "codal_IG",
                    "codal_RT",
                    "publisher_state",
                )
            },
        ),
    )

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: CodalCompany):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: CodalCompany):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
