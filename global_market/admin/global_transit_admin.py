import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from global_market.models import GlobalTransit


@admin.register(GlobalTransit)
class GlobalTransitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transit_type",
        "transit_unit",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = ("id", "transit_type", "transit_unit")

    ordering = ("-updated_at",)

    search_fields = ("transit_type", "transit_unit")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: GlobalTransit):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: GlobalTransit):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
