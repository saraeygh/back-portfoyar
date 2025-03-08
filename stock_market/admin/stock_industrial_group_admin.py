import pytz
import jdatetime
from persiantools.jdatetime import JalaliDateTime

from django.contrib import admin
from stock_market.models import StockIndustrialGroup


@admin.register(StockIndustrialGroup)
class StockIndustrialGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "priority", "created_at_shamsi", "updated_at_shamsi")

    list_display_links = ("id", "code", "name")

    ordering = ("-updated_at",)

    search_fields = ("id", "code", "name", "priority")

    @admin.display(description="ایجاد")
    def created_at_shamsi(self, obj: StockIndustrialGroup):
        shamsi = (
            JalaliDateTime(obj.created_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi

    @admin.display(description="به‌روزرسانی")
    def updated_at_shamsi(self, obj: StockIndustrialGroup):
        shamsi = (
            JalaliDateTime(obj.updated_at, tzinfo=pytz.UTC)
            + jdatetime.timedelta(hours=3, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return shamsi
