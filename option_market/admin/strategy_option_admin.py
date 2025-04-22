import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from option_market.models import StrategyOption


@admin.register(StrategyOption)
class StrategyOptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "key",
        "profit_status",
        "risk_level",
        "sequence",
        "created_at_shamsi",
        "updated_at_shamsi",
    )

    list_display_links = ("id", "name")

    ordering = ("risk_level",)

    search_fields = ("name", "key")

    list_filter = ("profit_status", "risk_level")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: StrategyOption):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: StrategyOption):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y/%m/%d %H:%M:%S")

        return shamsi
